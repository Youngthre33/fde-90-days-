# Day 75：使用 FastAPI 路径参数

## 学习目标

Day 74 的 `/` 和 `/health` 都是固定路由。Day 75 使用一条动态路由接收不同的工单 ID：

```text
GET /tickets/101
GET /tickets/205
GET /tickets/9999
```

它们由同一条 FastAPI 路由处理：

```python
@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: int = Path(ge=1)):
    return {
        "ticket_id": ticket_id
    }
```

## 三种路径写法

```text
旧 API 文档中的占位写法： /tickets/:id
FastAPI 路由声明：          /tickets/{ticket_id}
浏览器发送的真实地址：      /tickets/101
```

真实请求中要使用具体 ID，不能把 `{ticket_id}` 原样输入浏览器。

## 请求流程

```text
浏览器发送 GET /tickets/101
→ Uvicorn 接收请求
→ FastAPI 用 /tickets/{ticket_id} 匹配路径
→ 从 URL 中取出文本 "101"
→ 根据 int 转换成整数 101
→ 根据 Path(ge=1) 检查最小值
→ 调用 get_ticket(ticket_id=101)
→ 返回 Python 字典
→ FastAPI 转换成 JSON 响应
```

路径中的 `{ticket_id}` 和函数参数 `ticket_id` 使用相同名称，FastAPI 才能把取得的值交给对应参数。

## 类型转换与范围校验

```python
ticket_id: int = Path(ge=1)
```

- `int` 要求值能够转换成整数。
- `Path(...)` 配置路径参数。
- `ge` 是 greater than or equal 的缩写。
- `ge=1` 要求工单 ID 大于或等于 1。

FastAPI 会在调用 `get_ticket()` 之前完成转换和校验。输入不合法时，FastAPI 自动返回验证错误，路由函数不会执行。

## 200、422 与 404

| 请求 | 状态码 | 原因 |
|---|---:|---|
| `GET /tickets/1` | `200` | 是整数，并且达到最小值 |
| `GET /tickets/101` | `200` | 是合法正整数 |
| `GET /tickets/0` | `422` | 可以转换成整数，但小于 1 |
| `GET /tickets/-5` | `422` | 可以转换成整数，但小于 1 |
| `GET /tickets/abc` | `422` | 无法转换成整数 |
| `GET /tickets/101/extra` | `404` | 多出一个路径段，没有路由匹配 |
| `GET /tickets/9999` | `200` | 当前只校验并返回 ID，没有查询真实工单 |

`422` 表示路由已经匹配，但输入没有通过转换或验证。`404` 在本节表示没有路由匹配请求结构。

`/tickets/9999` 返回 `200` 只能证明 `9999` 是合法 ID 格式，不能证明该工单真实存在。判断资源是否存在需要加入工单数据和查找逻辑。

## 验证错误的结构

访问 `/tickets/0` 时，FastAPI 返回的错误中包含：

```json
{
  "type": "greater_than_equal",
  "loc": [
    "path",
    "ticket_id"
  ],
  "msg": "Input should be greater than or equal to 1",
  "input": "0"
}
```

- `type` 表示错误类型。
- `loc` 表示错误位于路径参数 `ticket_id`。
- `msg` 是错误说明。
- `input` 是实际收到的输入。

## 自动文档

`/docs` 会根据路由和类型标注，自动把 `ticket_id` 显示为：

```text
位置：path
必填：true
类型：integer
最小值：1
```

对应的 `/openapi.json` 包含：

```json
{
  "name": "ticket_id",
  "in": "path",
  "required": true,
  "schema": {
    "type": "integer",
    "minimum": 1
  }
}
```

这说明同一份 Python 声明同时用于运行时校验和接口文档生成。

## 启动命令

已激活虚拟环境时，在仓库根目录运行：

```powershell
python -m uvicorn main:app --app-dir day75 --host 127.0.0.1 --port 8000 --reload
```

没有激活虚拟环境时可以直接指定解释器：

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir day75 --host 127.0.0.1 --port 8000 --reload
```

## 当前范围

当前接口负责接收、转换、校验并返回路径中的工单 ID。后续课程会继续加入查询参数、真实工单数据、资源查找和不存在资源的 404 响应。
