# Day 77：根据 ID 查询真实工单并处理 404

## 这一节要解决什么问题

Day 75 的单张工单接口只能把路径中的 ID 原样返回：

```text
GET /tickets/999
→ {"ticket_id": 999}
```

但 `999` 只是一个合法的正整数，内存中的工单列表并没有这张工单。一个真正的查询接口应当区分两种结果：

```text
找到指定 ID 的工单
→ 返回完整工单和 200

没有找到指定 ID 的工单
→ 返回错误信息和 404
```

本节让 `GET /tickets/{ticket_id}` 真正查询内存中的 `tickets` 列表，并让程序的实际响应与 `/docs` 中的接口说明保持一致。

## 当前工单数据

程序启动并导入 `main.py` 时，会在 Python 进程的内存中创建四张工单：

| ID | 标题 | 状态 |
|---:|---|---|
| 101 | API 登录失败 | `open` |
| 102 | API 修改发票 | `in_progress` |
| 103 | 支付失败 | `open` |
| 104 | 导出报表失败 | `done` |

这些数据还没有保存到数据库或文件。服务器进程停止后，内存数据也会消失。

Day 76 的集合查询接口仍然保留：

```text
GET /tickets
GET /tickets?status=open&limit=2
```

Day 77 新增的重点是查询其中一张真实工单：

```text
GET /tickets/101
```

## 单张工单查询代码

```python
@app.get(
    "/tickets/{ticket_id}",
    responses={
        404: {
            "description": "工单不存在"
        }
    }
)
def get_ticket(ticket_id: int = Path(ge=1)):
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket

    raise HTTPException(
        status_code=404,
        detail="工单不存在"
    )
```

`{ticket_id}` 是路径参数。真实请求中的这一部分会交给函数参数 `ticket_id`：

```text
/tickets/102
         ↓
ticket_id = 102
```

`ticket_id: int` 要求这个值能够转换为整数，`Path(ge=1)` 进一步要求它大于或等于 1。

## 查找工单的执行流程

以请求 `/tickets/102` 为例：

```text
请求匹配 /tickets/{ticket_id}
→ 字符串 "102" 转换为整数 102
→ 102 通过 ge=1 的范围验证
→ 调用 get_ticket(ticket_id=102)
→ for 循环依次取出列表中的工单
→ 101 与 102 不相等，继续循环
→ 102 与 102 相等，找到目标工单
→ return ticket
→ FastAPI 把工单转换为 JSON，并返回 200
```

成功响应为：

```json
{
  "id": 102,
  "title": "API 修改发票",
  "status": "in_progress"
}
```

## `for` 循环中的 `return`

```python
for ticket in tickets:
    if ticket["id"] == ticket_id:
        return ticket
```

每轮循环中的 `ticket` 是当前正在检查的工单对象。比较表达式：

```python
ticket["id"] == ticket_id
```

只会得到 `True` 或 `False`：

- `False`：当前工单不是目标，继续检查下一张。
- `True`：找到了目标，`return ticket` 返回当前完整工单。

`return` 不只会返回数据，还会立即结束整个 `get_ticket()` 函数。找到目标以后，后面的工单不需要继续检查。

## 找不到时为什么要主动返回 404

以 `/tickets/999` 为例：

```text
999 是合法的正整数
→ 参数验证通过
→ get_ticket() 开始执行
→ for 循环检查完 101、102、103、104
→ 没有任何 ID 等于 999
→ 循环结束
→ raise HTTPException(...)
→ 返回 404
```

代码是：

```python
raise HTTPException(
    status_code=404,
    detail="工单不存在"
)
```

它有三个作用：

1. 立即停止当前函数的正常执行；
2. 让 FastAPI 返回 HTTP 状态码 `404`；
3. 把 `detail` 放进 JSON 响应正文。

实际响应为：

```json
{
  "detail": "工单不存在"
}
```

如果循环结束后既没有 `return`，也没有 `raise`，Python 函数会默认返回 `None`。在当前接口中，这可能让客户端得到 `200` 和 `null`，无法正确表达“工单不存在”。因此这里必须主动产生业务错误。

## `raise` 必须放在整个循环之后

正确位置：

```python
for ticket in tickets:
    if ticket["id"] == ticket_id:
        return ticket

raise HTTPException(...)
```

只有检查完所有工单仍未找到，才能确认目标不存在。

下面的写法是错误的：

```python
for ticket in tickets:
    if ticket["id"] == ticket_id:
        return ticket

    raise HTTPException(...)
```

如果 `raise` 位于循环内部，那么第一张工单不匹配时，函数就会立即返回 404，后面的工单没有机会被检查。例如查询 102 时，程序检查 101 后就会错误地停止。

## 请求经过的四个阶段

一次请求进入 FastAPI 后，可以按下面的顺序理解：

```text
1. 路由匹配
→ 2. 参数转换和验证
→ 3. 执行路由函数中的业务逻辑
→ 4. 生成并返回 HTTP 响应
```

不同错误会停在不同阶段：

| 请求 | 路由匹配 | 参数验证 | 是否执行 `get_ticket()` | 结果 |
|---|---|---|---|---|
| `/tickets/101` | 通过 | 通过 | 执行并找到 | `200` |
| `/tickets/999` | 通过 | 通过 | 执行但没找到 | 业务 `404` |
| `/tickets/0` | 通过 | 失败 | 不执行 | `422` |
| `/tickets/abc` | 通过 | 失败 | 不执行 | `422` |
| `/tickets/101/extra` | 失败 | 不进行 | 不执行 | 路由 `404` |

## 区分 422 与 404

### 参数错误：422

```text
GET /tickets/0
GET /tickets/abc
```

- `0` 不满足 `ge=1`。
- `abc` 不能转换为 `int`。

FastAPI 会在调用函数之前自动返回 `422 Unprocessable Entity`，因此 `get_ticket()` 中的循环不会执行。

### 资源不存在：业务 404

```text
GET /tickets/999
```

`999` 是合法的正整数，所以参数验证通过并进入函数。但列表中没有这张工单，函数主动 `raise HTTPException`，返回：

```json
{
  "detail": "工单不存在"
}
```

### 路径不存在：路由 404

```text
GET /tickets/101/extra
```

应用没有登记这个完整路径，所以请求在路由匹配阶段就失败了，`get_ticket()` 不会执行。FastAPI 返回：

```json
{
  "detail": "Not Found"
}
```

两种 404 的状态码相同，但来源不同：

| 类型 | 是否进入函数 | 产生者 | 响应信息 |
|---|---:|---|---|
| 业务 404 | 是 | `raise HTTPException(...)` | `工单不存在` |
| 路由 404 | 否 | FastAPI 路由系统 | `Not Found` |

## `responses` 为什么存在

装饰器中增加了：

```python
responses={
    404: {
        "description": "工单不存在"
    }
}
```

它的目的只有一个：**补充 OpenAPI 接口文档**。

FastAPI 能从 `ticket_id: int = Path(ge=1)` 自动知道参数可能验证失败，所以文档会自动列出 `422`。但是业务 404 写在函数内部的循环和 `raise` 中，FastAPI 不会自动分析所有业务分支来推断它。

添加 `responses` 后，FastAPI 会把这项说明写入 `/openapi.json`，Swagger UI 的 `/docs` 页面就能显示：

```text
404  工单不存在
```

这对前端开发者、测试人员以及其他接口调用者有用，因为他们能提前知道这个接口还可能返回 404，并编写对应的处理逻辑。

## `responses` 不会产生真实错误

必须分清这两段代码的职责：

| 代码 | 职责 |
|---|---|
| `responses={404: ...}` | 告诉 `/docs`：接口可能返回 404 |
| `raise HTTPException(status_code=404, ...)` | 请求发生时真正返回 404 |

如果删除 `responses`，保留 `raise HTTPException`：

```text
程序仍然会真正返回 404
但 /docs 中缺少这项说明
```

如果保留 `responses`，删除 `raise HTTPException`：

```text
/docs 仍会写着 404
但程序不会因为文档写了 404 就自动产生 404
```

所以 `responses` 是说明书，`raise HTTPException` 才是程序行为。

## 启动服务器

在仓库根目录执行。

已经激活虚拟环境时：

```powershell
python -m uvicorn main:app --app-dir day77 --host 127.0.0.1 --port 8000 --reload
```

没有激活虚拟环境时：

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir day77 --host 127.0.0.1 --port 8000 --reload
```

打开自动文档：

```text
http://127.0.0.1:8000/docs
```

## 手动测试

可以直接用浏览器访问，也可以新开一个 PowerShell 终端使用 `curl.exe`：

```powershell
curl.exe -i http://127.0.0.1:8000/tickets/101
curl.exe -i http://127.0.0.1:8000/tickets/104
curl.exe -i http://127.0.0.1:8000/tickets/999
curl.exe -i http://127.0.0.1:8000/tickets/0
curl.exe -i http://127.0.0.1:8000/tickets/abc
curl.exe -i http://127.0.0.1:8000/tickets/101/extra
```

预期结果：

| 请求 | 状态码 | 响应重点 |
|---|---:|---|
| `/tickets/101` | `200` | 返回 ID 101 的完整工单 |
| `/tickets/104` | `200` | 返回 ID 104 的完整工单 |
| `/tickets/999` | `404` | `{"detail":"工单不存在"}` |
| `/tickets/0` | `422` | 小于允许的最小值 1 |
| `/tickets/abc` | `422` | 无法转换为整数 |
| `/tickets/101/extra` | `404` | `{"detail":"Not Found"}` |

在 `/docs` 的 `GET /tickets/{ticket_id}` 中，还应看到文档列出的 `200`、`404` 和 `422`。文档中的状态说明与实际请求结果是两个需要分别验证的部分。

## 本节完成后的能力

完成 Day 77 后，应当能够解释：

1. 路径参数如何变成函数参数；
2. `for` 循环如何按 ID 查找对象；
3. 为什么找到后可以立即 `return`；
4. 为什么找不到时要主动 `raise HTTPException`；
5. 为什么 `raise` 必须位于循环外部；
6. 参数 `422`、业务 `404`、路由 `404` 分别在哪里产生；
7. `responses` 只补充 OpenAPI 文档，不能代替真正的错误处理。

## 当前范围

本节查询的是当前 Python 进程内存中的列表。还没有连接数据库，也没有为响应建立专门的数据模型。后续会继续把这些接口逐步发展成结构更完整的后端 API。
