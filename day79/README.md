# Day 79：用响应模型规定输出结构

## 这一节解决什么问题

Day 78 已经能够接收请求正文并创建工单，但接口函数返回的仍然只是普通字典：

```python
return created_ticket
```

如果没有响应模型，接口没有明确声明服务器承诺返回哪些字段、字段是什么类型，也可能把只供服务器内部使用的字段直接暴露给客户端。

Day 79 为工单接口增加 Pydantic 响应模型，让请求和响应分别具有明确的数据边界：

```text
TicketCreate
→ 规定客户端可以提交什么

Ticket
→ 规定服务器承诺返回什么
```

## 输入模型与响应模型

```python
class TicketCreate(BaseModel):
    title: str = Field(min_length=1)


class Ticket(BaseModel):
    id: int
    title: str
    status: Literal["open", "in_progress", "done"]
```

两个模型的职责不同：

| 模型 | 数据方向 | 字段 |
|---|---|---|
| `TicketCreate` | 客户端 → 服务器 | `title` |
| `Ticket` | 服务器 → 客户端 | `id`、`title`、`status` |

客户端只提交创建工单所需的标题：

```json
{
  "title": "客户无法下载发票"
}
```

服务器生成 ID 和默认状态后，返回完整工单：

```json
{
  "id": 105,
  "title": "客户无法下载发票",
  "status": "open"
}
```

## 把模型连接到接口

仅仅定义 `Ticket` 类不会自动影响任何接口。必须通过 `response_model` 把它连接到路由。

创建接口返回一张工单：

```python
@app.post(
    "/tickets",
    response_model=Ticket,
    status_code=201
)
```

列表接口返回多张工单组成的数组：

```python
@app.get(
    "/tickets",
    response_model=list[Ticket]
)
```

单张查询接口返回一张工单：

```python
@app.get(
    "/tickets/{ticket_id}",
    response_model=Ticket,
    responses={
        404: {
            "description": "工单不存在"
        }
    }
)
```

可以按返回数量选择模型：

| 返回内容 | 响应模型 |
|---|---|
| 一张完整工单 | `Ticket` |
| 多张完整工单 | `list[Ticket]` |

## `response_model=Ticket` 的含义

在装饰器调用中：

```python
response_model=Ticket
```

左边的 `response_model` 是 FastAPI 提供的参数，右边的 `Ticket` 是前面定义的 Pydantic 模型类。它的含义是：

> 当前接口正常返回数据时，使用 `Ticket` 模型检查、整理和说明响应。

路由函数仍然可以返回普通字典：

```python
return created_ticket
```

FastAPI 会在函数返回之后、向客户端发送响应之前应用 `Ticket` 模型。

## 响应模型的三个作用

### 1. 生成准确文档

Swagger 中会分别显示：

- `POST /tickets` 的请求正文是 `TicketCreate`；
- `POST /tickets` 的 201 响应是 `Ticket`；
- `GET /tickets` 的 200 响应是 `Ticket` 数组；
- `GET /tickets/{ticket_id}` 的 200 响应是 `Ticket`。

前端开发者不需要阅读服务器源代码，也能知道应该发送和接收什么。

### 2. 过滤未公开字段

实验中曾临时让内部对象包含：

```python
{
    "id": 105,
    "title": "用户无法修改收货地址",
    "status": "open",
    "internal_note": "只供服务器内部使用"
}
```

`Ticket` 没有声明 `internal_note`，所以连接响应模型的接口只向客户端返回：

```json
{
  "id": 105,
  "title": "用户无法修改收货地址",
  "status": "open"
}
```

响应模型规定了公开数据边界。它不会删除内存原对象中的额外字段，只会整理发送给客户端的响应。

### 3. 验证服务器输出

`Ticket` 规定状态只能是：

```text
open
in_progress
done
```

实验中把工单 101 的状态临时改成 `waiting` 后，路由函数虽然找到了并返回该字典，但响应模型验证失败，客户端得到 `500 Internal Server Error`，终端出现 `ResponseValidationError`。

把状态恢复为 `open` 后，请求重新返回 `200`。

## 区分输入 422 与输出 500

### 输入验证失败

```json
{
  "title": ""
}
```

执行顺序：

```text
TicketCreate 验证失败
→ create_ticket() 不执行
→ 返回 422
```

这表示客户端请求不符合接口要求。

### 输出验证失败

```python
{
    "id": 101,
    "title": "API 登录失败",
    "status": "waiting"
}
```

执行顺序：

```text
路由函数正常执行并返回字典
→ Ticket 响应验证失败
→ 返回 500
```

这表示服务器没有兑现自己声明的响应合同，属于服务器代码或内部数据问题。

| 出错位置 | 含义 | 常见状态码 |
|---|---|---:|
| 请求进入函数之前 | 客户端输入不合法 | `422` |
| 函数返回之后 | 服务器输出不合法 | `500` |

## `response_model` 与 `responses` 的区别

单张查询接口同时使用：

```python
response_model=Ticket,
responses={
    404: {
        "description": "工单不存在"
    }
}
```

两者职责不同：

| 设置 | 作用 |
|---|---|
| `response_model=Ticket` | 检查、过滤并记录正常成功响应的数据结构 |
| `responses={404: ...}` | 补充接口可能出现的 404 文档说明 |
| `raise HTTPException(status_code=404, ...)` | 请求发生时真正产生 404 |

## 完整请求与响应流程

```text
客户端发送 POST /tickets 和 JSON
→ TicketCreate 验证请求正文
→ FastAPI 把模型实例传给 ticket_to_create
→ create_ticket() 生成 ID 和 open 状态
→ append 到内存 tickets 数组
→ return created_ticket
→ Ticket 检查并过滤响应
→ FastAPI 序列化为 JSON
→ Uvicorn 向客户端返回 201
```

输入模型作用于函数调用之前，响应模型作用于函数返回之后。

## 启动服务器

在仓库根目录执行：

```powershell
python -m uvicorn day79.main:app --reload --port 8000
```

打开 Swagger：

```text
http://127.0.0.1:8000/docs
```

## 本节验证过的行为

| 场景 | 预期结果 |
|---|---|
| 正常创建工单 | `201`，返回 `Ticket` |
| 缺少标题 | `422`，创建函数不执行 |
| 空标题 | `422`，创建函数不执行 |
| 列出工单 | `200`，返回 `list[Ticket]` |
| 查询存在 ID | `200`，返回 `Ticket` |
| 查询不存在 ID | `404` |
| 内部对象含额外字段 | 公开响应排除该字段 |
| 内部状态违反 `Literal` | 响应验证失败并返回 `500` |

## 当前范围

- 数据仍然只保存在 Python 进程内存中；
- 服务器重启后新增数据会消失；
- 新 ID 仍由最后一张工单的 ID 加一生成；
- 当前完成了创建与读取接口的响应边界；
- 还没有接入数据库，也没有实现 FastAPI 版本的更新和删除接口。

## 本节完成后的能力

完成 Day 79 后，应当能够解释：

1. 为什么创建输入模型和完整工单响应模型不同；
2. `TicketCreate` 与 `Ticket` 分别作用于数据流的哪一边；
3. 为什么仅定义 `Ticket` 不会自动影响接口；
4. `response_model=Ticket` 中左右两边分别是什么；
5. 一张工单使用 `Ticket`、工单列表使用 `list[Ticket]` 的原因；
6. 响应模型怎样生成文档、过滤字段和验证服务器输出；
7. 输入验证失败的 422 与输出验证失败的 500 有什么区别；
8. `response_model`、`responses` 与 `raise HTTPException` 的不同职责。
