# Day 80：使用 PATCH 部分更新工单

## 这一节解决什么问题

前面的 FastAPI 接口已经能够创建和读取工单：

```text
POST /tickets
GET /tickets
GET /tickets/{ticket_id}
```

Day 80 增加更新能力：客户端可以只提交需要修改的标题、状态，或者同时提交两者，服务器保留没有提交的其他字段。

```http
PATCH /tickets/101
```

只修改标题：

```json
{
  "title": "登录接口持续超时"
}
```

只修改状态：

```json
{
  "status": "in_progress"
}
```

## CRUD 当前进度

| 字母 | 含义 | HTTP 方法 | 当前状态 |
|---|---|---|---|
| C | Create，创建 | `POST` | 已完成 |
| R | Read，读取 | `GET` | 已完成 |
| U | Update，更新 | `PATCH` | Day 80 完成 |
| D | Delete，删除 | `DELETE` | 后续完成 |

## 为什么需要新的更新模型

创建工单时标题是必填字段：

```python
class TicketCreate(BaseModel):
    title: str = Field(min_length=1)
```

PATCH 可能只修改状态，此时不能强制客户端同时提交标题。因此需要新的输入模型：

```python
class TicketUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    status: Literal["open", "in_progress", "done"] | None = None
```

三个模型的职责是：

| 模型 | 用途 |
|---|---|
| `TicketCreate` | 创建工单的输入，标题必填 |
| `TicketUpdate` | 部分更新的输入，标题和状态都可以省略 |
| `Ticket` | 服务器返回的完整工单 |

## 类型中的 `None` 与默认值 `None`

```python
title: str | None = Field(default=None, min_length=1)
```

两个 `None` 解决不同问题：

```text
str | None
→ 规定值可以是字符串或 None

default=None
→ 客户端没有提交该字段时，使用 None 作为默认值
```

只有 `str | None` 时，字段仍可能是必填的，只是允许客户端明确提交 `null`。增加默认值后，字段本身可以省略。

## PATCH 路由

```python
@app.patch(
    "/tickets/{ticket_id}",
    response_model=Ticket,
    responses={
        404: {
            "description": "工单不存在"
        }
    }
)
def update_ticket(
    ticket_to_update: TicketUpdate,
    ticket_id: int = Path(ge=1)
):
    update_data = ticket_to_update.model_dump(
        exclude_unset=True,
        exclude_none=True
    )

    for ticket in tickets:
        if ticket["id"] == ticket_id:
            ticket.update(update_data)
            return ticket

    raise HTTPException(
        status_code=404,
        detail="工单不存在"
    )
```

函数同时接收两种来源的数据：

```text
URL /tickets/101
→ ticket_id = 101

JSON 请求正文
→ TicketUpdate 验证
→ ticket_to_update
```

## `model_dump()` 的作用

`ticket_to_update` 是 Pydantic 模型实例，不是普通字典。`model_dump()` 会把模型数据导出为 Python 字典：

```text
TicketUpdate 模型对象
→ model_dump()
→ 普通 Python 字典
```

如果客户端只提交标题，无参数的 `model_dump()` 可能得到：

```python
{
    "title": "登录接口持续超时",
    "status": None
}
```

这会让 `status=None` 错误覆盖原状态。PATCH 需要只保留本次真正要修改的字段，所以使用：

```python
ticket_to_update.model_dump(
    exclude_unset=True,
    exclude_none=True
)
```

其中：

- `exclude_unset=True` 排除客户端没有提交的字段；
- `exclude_none=True` 排除值为 `None` 的字段。

输入与结果示例：

| 请求正文 | `update_data` |
|---|---|
| `{"title":"新标题"}` | `{"title":"新标题"}` |
| `{"status":"done"}` | `{"status":"done"}` |
| `{"title":"新标题","status":"done"}` | 两个字段都保留 |
| `{}` | `{}` |
| `{"title":null}` | `{}` |

POST 目前不需要 `model_dump()`，因为创建函数会直接读取 `ticket_to_create.title`，再手动组成包含 ID、标题和状态的新字典。POST 也可以使用 `model_dump()`，只是当前只有一个输入字段，明确读取属性更直观。

## `dict.update()` 的作用

找到目标工单后执行：

```python
ticket.update(update_data)
```

`ticket` 是要修改的原字典，`update_data` 是本次修改的小字典。`update()` 会覆盖其中出现的键，保留没有出现的键。

原工单：

```python
{
    "id": 101,
    "title": "API 登录失败",
    "status": "open"
}
```

更新数据：

```python
{
    "title": "登录接口持续超时"
}
```

更新结果：

```python
{
    "id": 101,
    "title": "登录接口持续超时",
    "status": "open"
}
```

循环中的 `ticket` 与 `tickets` 数组中对应的字典是同一个对象，因此 `ticket.update()` 会直接修改数组中的原工单。

`update()` 返回 `None`，所以不能写成：

```python
ticket = ticket.update(update_data)
```

## 为什么不能使用 `append()`

```python
tickets.append(created_ticket)
```

用于 POST，因为它要向列表中增加一张新工单。

```python
ticket.update(update_data)
```

用于 PATCH，因为它要修改已经存在的工单字典。

| 对象 | 类型 | 方法 | 作用 |
|---|---|---|---|
| `tickets` | `list` | `append()` | 增加新工单 |
| `ticket` | `dict` | `update()` | 修改已有工单的键值 |

PATCH 如果使用 `tickets.append(update_data)`，会增加一个缺少 ID 和状态的不完整对象，而不是更新目标工单。

## 成功路径

```text
PATCH /tickets/101
→ int 与 Path 验证 ticket_id
→ TicketUpdate 验证请求正文
→ model_dump() 生成本次更新字典
→ for 循环按 ID 查找真实工单
→ ticket.update(update_data)
→ return 完整工单
→ Ticket 响应模型检查
→ 返回 200
```

## 错误路径

| 请求 | 结果 | 是否进入函数 | 原因 |
|---|---:|---:|---|
| `ticket_id=0` | `422` | 否 | 不满足 `Path(ge=1)` |
| `ticket_id=abc` | `422` | 否 | 无法转换成 `int` |
| `status=waiting` | `422` | 否 | 不符合 `Literal` |
| `title=""` | `422` | 否 | 不满足 `min_length=1` |
| `ticket_id=999` | `404` | 是 | 遍历后找不到真实工单 |

错误输入在修改操作之前就被拦截，因此不会污染内存数据。

## 空更新和 `null`

当前版本中：

```json
{}
```

会得到空的 `update_data`，`ticket.update({})` 不做修改并返回原工单和 `200`。

```json
{
  "title": null
}
```

会因为 `exclude_none=True` 排除标题，同样不做修改。以后如果产品要求 PATCH 至少必须包含一个有效修改字段，可以再主动返回 `400`。

## 启动服务器

在仓库根目录执行：

```powershell
python -m uvicorn day80.main:app --reload --port 8000
```

打开 Swagger：

```text
http://127.0.0.1:8000/docs
```

## 本节测试范围

- 只修改标题，状态保持不变；
- 只修改状态，标题保持不变；
- 同时修改标题和状态；
- 非法状态返回 422；
- 空标题返回 422；
- ID 0 和文本 ID 返回 422；
- 不存在 ID 返回 404；
- 空对象和 `null` 不修改原工单；
- GET 能读取 PATCH 后的新数据；
- 服务器重启后内存数据恢复初始值。

## 当前范围

- 数据仍保存在 Python 进程内存中；
- PATCH 直接修改内存字典；
- 当前没有数据库事务或持久化；
- 当前允许空 PATCH 成功但不发生修改；
- 下一步将补齐 FastAPI 版本的 DELETE 操作。

## 本节完成后的能力

完成 Day 80 后，应当能够解释：

1. PATCH 与 POST 的业务区别；
2. 为什么更新需要独立的 `TicketUpdate` 输入模型；
3. 类型中的 `None` 与默认值 `None` 分别解决什么问题；
4. `model_dump()` 怎样把模型转换成字典；
5. 为什么 PATCH 使用 `exclude_unset` 和 `exclude_none`；
6. `dict.update()` 怎样只覆盖本次提交的键；
7. 为什么创建使用 `append()`、更新使用 `update()`；
8. 422 与 404 分别在哪个阶段产生；
9. 为什么错误请求不会修改原工单。
