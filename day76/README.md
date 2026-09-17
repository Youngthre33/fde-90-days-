# Day 76：使用 FastAPI 查询参数筛选工单

## 学习目标

路径参数用于指定某个资源：

```text
GET /tickets/101
```

查询参数用于筛选或控制资源集合：

```text
GET /tickets?status=open
GET /tickets?limit=2
GET /tickets?status=open&limit=1
```

查询字符串从 `?` 开始，多个参数用 `&` 分隔。FastAPI 根据参数名称读取值，所以查询参数的先后顺序不影响结果。

## 当前工单数据

本节使用四张保存在 Python 进程内存中的工单：

| ID | 标题 | 状态 |
|---:|---|---|
| 101 | API 登录失败 | `open` |
| 102 | API 修改发票 | `in_progress` |
| 103 | 支付失败 | `open` |
| 104 | 导出报表失败 | `done` |

这些数据在启动应用、导入 `main.py` 时创建。当前没有数据库或文件持久化。

## 查询参数函数

```python
@app.get("/tickets")
def get_tickets(
    status: Literal["open", "in_progress", "done"] | None = None,
    limit: int = Query(
        default=10,
        ge=1,
        le=100
    )
):
    filtered_tickets = []

    for ticket in tickets:
        if status is None or ticket["status"] == status:
            filtered_tickets.append(ticket)

    return filtered_tickets[:limit]
```

函数参数没有出现在 `/tickets` 的路径大括号中，因此 FastAPI 把它们解释为查询参数。

## 可选状态筛选

```python
status: Literal["open", "in_progress", "done"] | None = None
```

- `Literal` 把有效状态限制为 `open`、`in_progress`、`done`。
- `| None` 允许没有状态筛选条件。
- `= None` 表示请求没有提供 `status` 时使用 `None`。
- `None` 不是第四种工单状态，也不是字符串 `"None"`。

不传状态时：

```text
GET /tickets
→ status is None
→ 保留全部工单
```

提供状态时：

```text
GET /tickets?status=open
→ 只保留 ticket["status"] == "open" 的工单
```

`all` 不是真实状态，因此新设计不接受 `?status=all`。查看全部工单时直接省略 `status`。

## 数量限制

```python
limit: int = Query(
    default=10,
    ge=1,
    le=100
)
```

- `int` 负责整数转换。
- `Query` 提供查询参数的默认值、范围验证和文档信息。
- `default=10` 表示不传 `limit` 时最多返回 10 条。
- `ge=1` 表示不能小于 1。
- `le=100` 表示不能大于 100。

即使不使用 `Query`，FastAPI 也能根据函数签名把 `limit` 识别为查询参数。这里使用 `Query` 是为了增加范围限制和 OpenAPI 信息。

## 筛选与截取流程

```text
创建空的 filtered_tickets
→ 遍历全部 tickets
→ 没有 status 时保留全部
→ 有 status 时只保留匹配项
→ 使用 [:limit] 截取结果前几项
→ 返回 JSON 数组
```

`filtered_tickets[:limit]` 是列表切片，表示从列表开头取到 `limit` 之前。例如 `[:2]` 返回索引 0 和 1，共两项。

当前实现会先遍历并筛选全部内存工单，再限制响应数量。真正使用数据库后，通常会把筛选和数量限制交给数据库执行。

## 为什么先筛选再限制数量

请求：

```text
GET /tickets?status=open&limit=2
```

正确顺序：

```text
全部工单
→ 筛选出 101、103
→ 截取前 2 条
→ 返回 101、103
```

如果先截取全部工单的前两条，再筛选状态，就会漏掉 ID 103。

## 实际结果

| 请求 | 状态码 | 结果 |
|---|---:|---|
| `/tickets` | `200` | 全部四张工单 |
| `/tickets?status=open` | `200` | 101、103 |
| `/tickets?status=in_progress` | `200` | 102 |
| `/tickets?status=done` | `200` | 104 |
| `/tickets?status=open&limit=1` | `200` | 101 |
| `/tickets?status=all` | `422` | `all` 不是真实状态 |
| `/tickets?status=opne` | `422` | 不在 Literal 允许值中 |
| `/tickets?status=` | `422` | 空字符串不在允许值中 |
| `/tickets?limit=0` | `422` | 小于最小值 1 |
| `/tickets?limit=101` | `422` | 大于最大值 100 |
| `/tickets?limit=abc` | `422` | 无法转换成整数 |

## 自动文档

`/docs` 和 `/openapi.json` 会显示：

- `status` 位于 `query`，不是必填项，允许三个状态或 `null`。
- `limit` 位于 `query`，不是必填项，默认值为 10，范围为 1 到 100。
- 非法查询值在路由函数执行前返回 422。

## 启动命令

已激活虚拟环境时：

```powershell
python -m uvicorn main:app --app-dir day76 --host 127.0.0.1 --port 8000 --reload
```

未激活虚拟环境时：

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir day76 --host 127.0.0.1 --port 8000 --reload
```

## 当前范围

本节已经让查询参数真正参与内存工单的筛选与数量控制。当前单张工单路由仍只返回 ID，还没有按 ID 查找工单；工单数据也没有持久化。
