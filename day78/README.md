# Day 78：通过请求正文创建工单

## 这一节解决什么问题

前面的课程已经让服务器能够读取工单：

```text
GET /tickets
GET /tickets/{ticket_id}
```

Day 78 开始实现写入功能：客户端只提交工单标题，服务器负责生成 ID、设置默认状态、把完整工单加入内存数组，并返回创建结果。

```text
客户端提交标题
→ POST /tickets
→ FastAPI 验证请求正文
→ 服务器生成 ID 和 open 状态
→ 加入 tickets 数组
→ 返回完整工单和 201
```

以前这个功能由 `json-server` 自动完成。现在我们开始自己编写服务器创建工单的规则。

## 请求正文模型

```python
class TicketCreate(BaseModel):
    title: str = Field(min_length=1)
```

`TicketCreate` 是创建工单时，请求正文必须遵守的数据模型：

- 请求正文必须有 `title`；
- `title` 必须通过字符串类型验证；
- `Field(min_length=1)` 要求字符串至少包含一个字符。

合法请求正文示例：

```json
{
  "title": "客户无法下载发票"
}
```

缺少 `title` 或使用空字符串时，FastAPI 会在调用创建函数之前返回 `422`：

```json
{}
```

```json
{
  "title": ""
}
```

## 创建工单接口

```python
@app.post(
    "/tickets",
    status_code=201
)
def create_ticket(ticket_to_create: TicketCreate):
    created_ticket = {
        "id": tickets[-1]["id"] + 1,
        "title": ticket_to_create.title,
        "status": "open"
    }

    tickets.append(created_ticket)

    return created_ticket
```

`@app.post("/tickets")` 把 `POST /tickets` 登记为创建接口。`status_code=201` 规定函数正常完成时使用 `201 Created`，准确表达服务器创建了新资源。

如果省略 `status_code=201`，创建逻辑仍能运行，但 FastAPI 默认会返回 `200 OK`。

## 请求正文怎样进入函数

函数参数是：

```python
ticket_to_create: TicketCreate
```

FastAPI 会读取这个类型标注，并在背后完成下面的工作：

```text
读取 HTTP 请求正文
→ 解析 JSON
→ 使用 TicketCreate 验证数据
→ 创建 TicketCreate 实例
→ 把实例传给 ticket_to_create
→ 调用 create_ticket(ticket_to_create)
```

因此，客户端提交：

```json
{
  "title": "客户无法下载发票"
}
```

以后，函数里的：

```python
ticket_to_create.title
```

就能读取经过验证的标题。

## 服务器怎样组成完整工单

客户端只负责提交标题。服务器负责生成不能交给客户端随意决定的数据：

```python
created_ticket = {
    "id": tickets[-1]["id"] + 1,
    "title": ticket_to_create.title,
    "status": "open"
}
```

`tickets[-1]` 取得数组中的最后一张工单，继续使用 `["id"]` 取得它的 ID，再加一得到临时的新 ID。

```text
最后一个 ID 是 104
→ tickets[-1]["id"] 得到 104
→ 104 + 1
→ 新 ID 是 105
```

这个办法目前只适合非空且按 ID 排好顺序的教学数组。真正接入数据库以后，通常由数据库生成唯一 ID。

服务器统一把新工单的初始状态设为：

```python
"status": "open"
```

## 把工单加入数组

```python
tickets.append(created_ticket)
```

`append()` 直接修改原来的 `tickets` 数组，把新对象放到末尾。它的返回值是 `None`，所以不能写成：

```python
tickets = tickets.append(created_ticket)
```

## 返回创建结果

```python
return created_ticket
```

FastAPI 会把 Python 字典转换为 JSON，并使用 `201` 返回给客户端：

```json
{
  "id": 105,
  "title": "客户无法下载发票",
  "status": "open"
}
```

## 一次成功请求的完整流程

```text
Swagger 或前端发送 POST /tickets
→ Uvicorn 在 8000 端口收到请求
→ FastAPI 匹配创建接口
→ 读取并解析 JSON 请求正文
→ TicketCreate 和 Field 验证 title
→ 验证成功后调用 create_ticket()
→ 生成 ID 和默认 open 状态
→ append 到 tickets 数组
→ return created_ticket
→ FastAPI 转换为 JSON
→ Uvicorn 返回 201 和响应正文
```

## 验证失败时为什么不会产生工单

发送：

```json
{}
```

或者：

```json
{
  "title": ""
}
```

都会在进入 `create_ticket()` 前得到 `422`。因此下面两步不会执行：

```python
created_ticket = {...}
tickets.append(created_ticket)
```

错误请求不会污染 `tickets` 数组。

## 为什么服务器重启后数据会恢复

当前 `tickets` 只是 Python 进程内存中的数组，没有写入文件或数据库：

```text
启动服务器
→ 根据源代码创建 4 张初始工单
→ POST 创建第 5 张工单
→ 内存中暂时有 5 张
→ 停止服务器进程
→ 进程内存消失
→ 再次启动并重新执行 main.py
→ 又从源代码中的 4 张开始
```

以后接入数据库后，服务器重启不会让已经保存的数据消失。

## 启动服务器

在仓库根目录执行：

```powershell
python -m uvicorn day78.main:app --reload --port 8000
```

打开 Swagger：

```text
http://127.0.0.1:8000/docs
```

## 手动测试结果

| 请求正文 | 预期状态码 | 是否创建 |
|---|---:|---:|
| `{"title":"客户无法下载发票"}` | `201` | 是 |
| `{}` | `422` | 否 |
| `{"title":""}` | `422` | 否 |

创建成功后访问：

```text
GET http://127.0.0.1:8000/tickets
```

应当能在列表末尾看到新工单。再访问：

```text
GET http://127.0.0.1:8000/tickets/105
```

应当能按 ID 查询刚创建的完整工单。

## 当前范围与已知限制

- 数据只保存在进程内存中，服务器重启后会恢复初始值；
- 新 ID 暂时通过最后一张工单的 ID 加一生成；
- `min_length=1` 能阻止 `""`，但只包含空格的字符串仍有至少一个字符，后续可以继续增加清理或自定义验证；
- 当前还没有专门的响应模型；
- 当前还没有数据库。

## 本节完成后的能力

完成 Day 78 后，应当能够解释：

1. `BaseModel` 和 `Field` 怎样规定请求正文结构；
2. FastAPI 怎样把 JSON 转成 `TicketCreate` 实例；
3. `ticket_to_create: TicketCreate` 中参数名、冒号和类型的关系；
4. 为什么客户端只提交标题，而服务器负责生成 ID 和状态；
5. `tickets[-1]["id"] + 1` 每一层取得的内容；
6. `append()` 怎样修改内存数组；
7. `201` 与默认 `200` 的区别；
8. 为什么错误输入得到 `422`，并且不会执行创建函数；
9. 为什么服务器重启后新工单会消失。
