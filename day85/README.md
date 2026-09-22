# Day85：使用 TestClient 测试 FastAPI 接口

## 本节目标

通过请求与响应验证 FastAPI 应用的对外行为，包括路由、参数和请求体校验、状态码、JSON 响应以及 CRUD 后的数据变化。

Day83、Day84 直接调用业务函数；本节使用 `TestClient(app)`，请求经过接口层后再进入业务层。测试在自己的进程中运行，不连接 Uvicorn 的监听端口，也不需要打开 Swagger。

## 文件与依赖

- `test_ticket_api.py`：接口测试和数据隔离 fixture。
- `../day82/main.py`：被测试的 FastAPI 应用。
- `../day82/ticket_service.py`、`../day82/ticket_store.py`：应用使用的业务函数和共享内存列表。
- `../day83/requirements.txt`：继续使用已有环境依赖快照，本节不重复创建依赖清单。

需要重建环境时，在仓库根目录执行：

```powershell
.\.venv\Scripts\python.exe -m pip install -r day83/requirements.txt
```

## 测试运行

在仓库根目录执行：

```powershell
.\.venv\Scripts\python.exe -m pytest day85/test_ticket_api.py -v
.\.venv\Scripts\python.exe -m pytest day83/test_ticket_service.py day84/test_ticket_mutations.py day85/test_ticket_api.py -v
```

完整写入本节十个测试后，预期分别为 `10 passed` 和 `19 passed`。如果只保存了前五个只读测试，则分别只有 `5 passed` 和 `14 passed`；这表示代码尚未补齐，不是已有断言失败。

## 十个接口测试

| 测试 | 请求与预期 |
|---|---|
| 健康检查 | GET /health 返回 200 和 status=ok |
| 查询存在工单 | GET /tickets/101 返回 200 和完整工单 |
| 查询不存在工单 | GET /tickets/999 返回 404 和工单不存在 |
| ID 为零 | GET /tickets/0 返回 422 |
| ID 为文本 | GET /tickets/abc 返回 422 |
| 创建成功 | POST /tickets 返回 201、ID 105、默认 open，随后 GET 能查回 |
| 空标题创建 | POST 提交空字符串标题返回 422，前后 GET 列表内容一致 |
| 修改标题 | PATCH /tickets/101 返回 200，保留 ID 和状态，随后 GET 能读到新标题 |
| 非法状态修改 | PATCH 提交 waiting 返回 422，前后 GET 工单内容一致 |
| 删除 | DELETE /tickets/103 返回 204 和空正文；随后查询及重复删除返回 404 |

## 关键写法

```python
client = TestClient(app)
response = client.post("/tickets", json={"title": "客户无法提供发票"})
```

`app` 是从 Day82 导入的 FastAPI 应用，`client` 是连接该应用的测试客户端。`json=` 指定请求正文，由客户端编码成 JSON。

- `response.status_code`：读取响应状态码。
- `response.json()`：解析响应正文中的 JSON，得到 Python 字典、列表等数据；这里是同步调用，不需要 await。
- `response.text`：以字符串读取正文，204 成功响应通过 `response.text == ""` 检查，不调用 `.json()`。
- 比较不同响应解析后的数据使用 `==`，不要求它们是同一个 Python 对象。

## 数据隔离

写接口会修改当前测试进程的共享列表，因此本模块使用与 Day84 相同的 `reset_tickets` fixture：

```text
备份数据内容
  → 原地替换共享列表为固定四张工单
  → yield 暂停，让 pytest 执行当前测试
  → 恢复数据内容
```

每个测试都独立从四张固定工单开始。新建工单预计是 105；一个测试修改或删除工单后，不应影响另一个测试的起始数据。

创建和修改后再发 GET，可以确认数据已经写入本测试进程的应用内存；不代表实现了数据库持久化。无效输入测试同时检查 422 和数据不变。

## 当前限制与后续

TestClient 验证应用在进程内的接口行为，不验证真实网络、Uvicorn 部署或浏览器行为。本节也不引入数据库。

当前依赖组合可能显示 Starlette 使用 httpx 的弃用提醒，以及 AnyIO BlockingPortal 别名的弃用提醒。已进行的示例验证中，这些提醒没有造成测试失败；依赖迁移应作为单独的、有验证的变更处理。

完整测试通过后，下一节进入配置与环境变量，学习把部署时可能变化的设置与业务代码分开。
