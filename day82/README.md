# Day 82：分离接口层、业务层和数据层

## 这一节解决什么问题

Day 81 已经完成内存版工单 API 的 CRUD：

```text
POST   /tickets             → 创建工单
GET    /tickets             → 查询工单列表
GET    /tickets/{ticket_id} → 查询单张工单
PATCH  /tickets/{ticket_id} → 修改工单
DELETE /tickets/{ticket_id} → 删除工单
```

这些功能都写在一个 `main.py` 中时，HTTP 处理、业务逻辑和数据保存混在一起。功能继续增加后，文件会越来越长，同一段查找代码也会在 GET、PATCH、DELETE 中重复出现。

Day 82 不改变用户能够使用的功能，而是将代码按职责拆成三层：

```text
接口层 → 业务层 → 数据层
```

## 目录结构

```text
day82/
├── __init__.py
├── main.py
├── ticket_service.py
└── ticket_store.py
```

| 文件 | 职责 |
|---|---|
| `main.py` | 定义 FastAPI 应用、请求模型、响应模型、路由、HTTP 状态码和异常 |
| `ticket_service.py` | 查找、筛选、创建、修改和删除工单 |
| `ticket_store.py` | 创建并保存当前进程中的 `tickets` 列表 |
| `__init__.py` | 将 `day82` 标记为可导入的 Python 包 |

## 三层请求路线

```text
Swagger、前端或其他客户端
             │
             │ HTTP 请求
             ▼
          Uvicorn
             │
             ▼
main.py：FastAPI 接口层
             │
             │ 调用普通 Python 函数
             ▼
ticket_service.py：业务层
             │
             │ 读取或修改共享列表
             ▼
ticket_store.py：数据层
             │
             ▼
       返回业务处理结果
             │
             ▼
main.py 将结果变成 HTTP 响应
             │
             ▼
Swagger、前端或其他客户端
```

## 数据层：只保存数据

`ticket_store.py` 中创建真实工单列表：

```python
tickets = [
    {
        "id": 101,
        "title": "API 登录失败",
        "status": "open"
    },
    # ...
]
```

业务层导入：

```python
from day82.ticket_store import tickets
```

这个导入不会自动复制第二份列表。`ticket_store.py` 中的 `tickets` 和业务层导入的 `tickets` 指向同一个列表对象。

因此下面的操作都会修改真实共享数据：

```python
tickets.append(created_ticket)
tickets.remove(ticket)
ticket.update(update_data)
```

但下面的重新赋值只会让当前名字指向另一个列表：

```python
tickets = new_list
```

原地修改对象和让变量改变指向是不同操作。

## 业务层：处理工单规则

`ticket_service.py` 提供五个业务函数：

| 函数 | 输入 | 成功返回 | 失败返回 |
|---|---|---|---|
| `find_ticket_by_id()` | 工单 ID | 找到的工单 | `None` |
| `list_tickets()` | 状态、数量限制 | 筛选后的列表 | 空列表也属于正常结果 |
| `create_new_ticket()` | 标题 | 新工单 | 当前版本没有单独失败分支 |
| `update_ticket_by_id()` | ID、更新字典 | 修改后的工单 | `None` |
| `delete_ticket_by_id()` | 工单 ID | 被删除的工单 | `None` |

业务层不使用 `HTTPException`、`Path` 或 `Query`。它只接收普通 Python 值并返回普通 Python 对象。

## 复用 ID 查找函数

```python
def find_ticket_by_id(ticket_id: int):
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket

    return None
```

GET、PATCH 和 DELETE 都需要根据 ID 找到真实工单，所以 PATCH 和 DELETE 复用这个函数，不再各写一遍循环。

找到时：

```python
return ticket
```

没有找到时：

```python
return None
```

业务层只表达“找到”或“没找到”。接口层再决定没找到应该返回 HTTP 404。

## service 的 `return` 到了哪里

以删除为例：

```python
# ticket_service.py
return ticket
```

调用位置是：

```python
# main.py
deleted_ticket = delete_ticket_by_id(ticket_id)
```

右侧函数调用的结果由 `return` 决定。业务函数中的 `ticket` 和接口层中的 `deleted_ticket` 是不同局部变量名，但它们先后指向同一个工单对象。

```text
service 的 ticket ──────────► 工单对象 A
                                  │ return
                                  ▼
main 的 deleted_ticket ─────► 同一个工单对象 A
```

函数返回的是对象，不是变量名。

## 接口层：负责 HTTP 边界

`main.py` 保留以下内容：

- `@app.get()`、`@app.post()`、`@app.patch()`、`@app.delete()`；
- 路径参数和查询参数；
- Pydantic 请求模型与响应模型；
- 200、201、204、404、422 等 HTTP 行为；
- 将业务层的 `None` 转成 `HTTPException(404)`。

例如查询单张工单：

```python
def get_ticket(ticket_id: int = Path(ge=1)):
    ticket = find_ticket_by_id(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="工单不存在"
        )

    return ticket
```

分工是：

```text
service：找不到时返回 None
main：把 None 转成 HTTP 404
```

## 校验为什么留在 main.py

列表路由仍在接口层规定：

```python
status: Literal["open", "in_progress", "done"] | None = None
limit: int = Query(default=10, ge=1, le=100)
```

FastAPI 根据这些信息完成真正的运行时校验并生成 Swagger 文档。

业务层只写：

```python
def list_tickets(
    status: str | None,
    limit: int,
):
```

这里的 `str | None` 和 `int` 是普通 Python 类型标注，主要说明业务函数希望收到什么数据；它们不会再次执行 FastAPI 的 `Literal`、`Query` 或 422 校验。

完整路线：

```text
URL 中的原始查询参数
        ↓
main.py / FastAPI 校验和转换
        ↓
已经合格的 str、None、int
        ↓
ticket_service.py 筛选和切片
```

## GET 列表流程

请求：

```text
GET /tickets?status=open&limit=1
```

流程：

```text
FastAPI 校验 status 和 limit
→ main.py 调用 list_tickets("open", 1)
→ service 遍历共享 tickets
→ 将 open 工单放进 filtered_tickets
→ 使用 [:1] 限制数量
→ 返回结果列表给 main.py
→ main.py 返回给 FastAPI
→ FastAPI 使用 list[Ticket] 生成 JSON
```

`filtered_tickets` 是新列表，但其中的工单字典仍然是原列表中的对象引用。这属于浅层列表组合，不会复制每一个工单字典。

## POST 创建流程

请求：

```json
{
  "title": "客户无法登录"
}
```

流程：

```text
FastAPI 使用 TicketCreate 校验请求体
→ main.py 读取 ticket_to_create.title
→ 调用 create_new_ticket(title)
→ service 生成 ID 和默认状态 open
→ service 将新字典 append 到共享 tickets
→ service 返回新工单给 main.py
→ main.py 返回新工单给 FastAPI
→ FastAPI 返回 201 Created
```

## PATCH 修改流程

请求：

```json
{
  "status": "done"
}
```

接口层先执行：

```python
update_data = ticket_to_update.model_dump(
    exclude_unset=True,
    exclude_none=True
)
```

它把 Pydantic 模型转换成普通字典，再交给业务层：

```python
updated_ticket = update_ticket_by_id(
    ticket_id,
    update_data
)
```

业务层查找真实工单并执行：

```python
ticket.update(update_data)
```

这会原地修改共享列表中的工单字典，不会创建新的 `tickets` 列表。

## DELETE 删除流程

```python
deleted_ticket = delete_ticket_by_id(ticket_id)
```

业务层执行：

```python
tickets.remove(ticket)
return ticket
```

真实列表已经删除该工单，返回被删除的对象只是为了让调用者判断删除是否成功。

接口层成功时执行裸 `return`，结合：

```python
status_code=204
```

FastAPI 返回：

```text
204 No Content
```

这不是没有响应，而是有成功状态码、没有 JSON 响应体。客户端需要最新列表时，可以本地移除该 ID，或再次执行 `GET /tickets`。

## 启动服务器

在仓库根目录、虚拟环境已激活时运行：

```powershell
python -m uvicorn day82.main:app --reload --port 8000
```

打开 Swagger：

```text
http://127.0.0.1:8000/docs
```

`day82.main:app` 表示：

```text
day82 → Python 包
main  → main.py 模块
app   → 模块中的 FastAPI 对象
```

## 本节验证范围

- Python 文件语法编译成功；
- FastAPI 应用能够正常导入；
- 5 条业务路由全部注册到 OpenAPI；
- GET 返回初始列表；
- `status` 筛选和 `limit` 切片正确；
- 非法状态、范围外 limit 和非整数参数返回 422；
- 查询存在工单返回 200；
- 查询不存在工单返回 404；
- POST 创建返回 201、新 ID 和默认 `open`；
- 无标题和空标题返回 422；
- PATCH 可以同时更新标题和状态；
- PATCH 不存在工单返回 404；
- 非法更新状态返回 422；
- DELETE 成功返回 204 且响应体为空；
- 删除后再次查询返回 404；
- 重复删除返回 404。

## 当前限制

- `tickets` 仍然保存在 Python 进程内存中；
- 服务器重启后数据恢复到 `ticket_store.py` 中的初始值；
- 还没有数据库、事务或并发写入保护；
- ID 仍根据当前列表最后一个工单计算；
- Pydantic 模型暂时仍保留在 `main.py` 中。

## 本节完成后的能力

完成 Day 82 后，应当能够解释：

1. `main.py`、`ticket_service.py`、`ticket_store.py` 分别负责什么；
2. 为什么 `main.py` 不再直接导入 `tickets`；
3. 多个模块怎样共同操作同一个列表对象；
4. 为什么 `return ticket` 返回的是对象，而不是变量名；
5. service 的返回值怎样被 main 中的变量接收；
6. 为什么 FastAPI 校验留在接口层；
7. 为什么 service 使用普通 Python 参数；
8. 为什么找不到时 service 返回 `None`，main 再转换成 404；
9. 为什么 DELETE 可以返回 204 空响应；
10. 分层为什么没有改变 API 功能，却提高了可读性和可维护性。
