# Day 81：使用 DELETE 删除工单

## 这一节解决什么问题

Day 81 为内存版 FastAPI Ticket API 增加删除能力，补齐创建、读取、更新、删除四种基本操作。

```text
POST   /tickets             → 创建
GET    /tickets             → 查询列表
GET    /tickets/{ticket_id} → 查询单张
PATCH  /tickets/{ticket_id} → 部分更新
DELETE /tickets/{ticket_id} → 删除
```

删除请求只需要 URL 中的工单 ID，不需要 JSON 请求正文。

## DELETE 路由

```python
@app.delete(
    "/tickets/{ticket_id}",
    status_code=204,
    responses={
        404: {
            "description": "工单不存在"
        }
    }
)
def delete_ticket(ticket_id: int = Path(ge=1)):
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            tickets.remove(ticket)
            return

    raise HTTPException(
        status_code=404,
        detail="工单不存在"
    )
```

同一路径可以根据请求方法执行不同功能：

```text
GET    /tickets/103 → 查询 103
PATCH  /tickets/103 → 修改 103
DELETE /tickets/103 → 删除 103
```

FastAPI 同时根据 HTTP 方法和路径选择路由函数。

## 为什么 DELETE 不需要请求模型

创建和更新需要读取 JSON 请求正文，所以分别使用：

```text
TicketCreate
TicketUpdate
```

DELETE 的目标已经由路径确定：

```text
DELETE /tickets/103
                ↓
ticket_id = 103
```

因此函数只需要：

```python
ticket_id: int = Path(ge=1)
```

它不接收请求正文，也不需要额外的 `TicketDelete` 模型。

## 查找和删除

```python
for ticket in tickets:
    if ticket["id"] == ticket_id:
        tickets.remove(ticket)
        return
```

循环逐个检查工单 ID。找到目标后：

```python
tickets.remove(ticket)
```

直接从原列表中移除该工单字典。

删除前：

```text
101、102、103、104
```

删除 103 后：

```text
101、102、104
```

`remove()` 会原地修改列表，不会创建新列表，也不需要给 `tickets` 重新赋值。

## CRUD 使用的三种原地修改

| 操作 | 代码 | 效果 |
|---|---|---|
| 创建 | `tickets.append(created_ticket)` | 给列表增加元素 |
| 更新 | `ticket.update(update_data)` | 修改已有字典中的键值 |
| 删除 | `tickets.remove(ticket)` | 从列表移除元素 |

PATCH 不能使用 `append()`，否则会增加一条不完整数据。DELETE 也不能使用 `update()`，因为目标是移除整个对象。

## 为什么成功状态码是 204

```python
status_code=204
```

`204 No Content` 表示请求成功，但没有响应正文。

删除成功后，客户端关心的是目标资源已经不存在，不一定需要服务器再次返回整个对象。

| 操作 | 成功状态码 | 响应正文 |
|---|---:|---|
| GET 查询 | `200` | 返回数据 |
| PATCH 更新 | `200` | 返回更新后的工单 |
| POST 创建 | `201` | 返回新工单 |
| DELETE 删除 | `204` | 空 |

成功响应没有正文，因此 DELETE 路由不需要 `response_model=Ticket`。

## 裸 `return` 的作用

删除完成后执行：

```python
return
```

裸 `return` 等同于返回 `None`，并立即结束函数。结合路由中的 `status_code=204`，FastAPI 会生成没有响应正文的 204 响应。

如果删除后没有立即结束函数，程序可能继续执行循环后的 404，因此成功删除后必须退出。

## 找不到时返回 404

只有检查完整个列表仍未找到目标，才执行：

```python
raise HTTPException(
    status_code=404,
    detail="工单不存在"
)
```

例如：

```text
DELETE /tickets/999
→ 999 可以转换成整数
→ 满足 ge=1
→ 进入 delete_ticket()
→ 遍历后找不到
→ 返回 404
```

`responses={404: ...}` 只补充 Swagger 文档；`raise HTTPException(...)` 才在真实请求中产生 404。

## 成功删除流程

```text
客户端发送 DELETE /tickets/103
→ Uvicorn 接收请求
→ FastAPI 匹配 DELETE 路由
→ int 转换与 Path(ge=1) 验证
→ 调用 delete_ticket(ticket_id=103)
→ for 循环找到工单 103
→ tickets.remove(ticket)
→ return 结束函数
→ 返回 204，无响应正文
```

## 失败路径

| 请求 | 结果 | 是否进入函数 | 原因 |
|---|---:|---:|---|
| `DELETE /tickets/0` | `422` | 否 | 不满足 `ge=1` |
| `DELETE /tickets/abc` | `422` | 否 | 无法转换成整数 |
| `DELETE /tickets/999` | `404` | 是 | 遍历后找不到真实工单 |
| 重复删除已经删除的 ID | `404` | 是 | 第二次目标已不存在 |

## DELETE 的幂等性

第一次删除：

```text
DELETE /tickets/103
→ 204
→ 工单 103 不存在
```

第二次删除：

```text
DELETE /tickets/103
→ 404
→ 工单 103 仍然不存在
```

两次响应状态码可以不同，但重复执行后的资源最终状态相同，所以 DELETE 具有幂等性。

幂等性比较的是最终资源状态，不要求每一次响应完全一样。

## 内存数据的限制

删除只修改当前 Python 进程中的 `tickets` 列表：

```text
启动服务器 → 101、102、103、104
删除 103   → 101、102、104
停止进程   → 当前内存消失
重新启动   → 根据源代码恢复 101、102、103、104
```

以后接入数据库后，删除结果才会跨服务器重启保留。

## 启动服务器

在仓库根目录执行：

```powershell
python -m uvicorn day81.main:app --reload --port 8000
```

打开 Swagger：

```text
http://127.0.0.1:8000/docs
```

## 本节测试范围

- 初始列表包含 101、102、103、104；
- 删除 103 返回 204 且正文为空；
- 列表中不再包含 103；
- 查询已删除的 103 返回 404；
- 再次删除 103 返回 404；
- 删除 0 和文本 ID 返回 422；
- 删除不存在的 999 返回 404；
- 其他工单保持不变；
- 服务器重启后内存数据恢复初始值。

## 当前范围

- FastAPI 内存版 CRUD 已完整运行；
- 所有修改仍只存在于 Python 进程内存；
- 还没有把路由逻辑拆分成业务层与数据层；
- 还没有使用数据库或事务。

## 本节完成后的能力

完成 Day 81 后，应当能够解释：

1. DELETE 为什么只需要路径 ID；
2. 为什么成功删除可以使用 204；
3. 为什么 204 不需要响应模型；
4. `tickets.remove(ticket)` 怎样修改原列表；
5. 为什么成功删除后要立即 `return`；
6. 422 与 404 在删除流程中的不同来源；
7. 为什么重复 DELETE 的状态码不同仍然具有幂等性；
8. 为什么服务器重启后被删除的内存数据会恢复。
