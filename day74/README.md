# Day 74：创建第一个 FastAPI 服务

## 学习目标

Day 73 完成了 Python 虚拟环境和依赖安装。Day 74 把硬盘上的 FastAPI、Uvicorn 和 Python 代码连接成一个真正运行的本地 API 服务：

```text
Python 执行 main.py
→ 创建 FastAPI 应用对象
→ 登记路由
→ Uvicorn 监听 127.0.0.1:8000
→ 接收 HTTP 请求
→ FastAPI 执行对应函数
→ 返回 JSON 响应
```

## 启动命令

在仓库根目录执行：

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir day74 --host 127.0.0.1 --port 8000 --reload
```

命令各部分的作用：

| 部分 | 作用 |
|---|---|
| `.\.venv\Scripts\python.exe` | 使用项目虚拟环境中的 Python |
| `-m uvicorn` | 运行已安装的 Uvicorn |
| `main:app` | 从 `main.py` 中取得名为 `app` 的应用对象 |
| `--app-dir day74` | 到 `day74` 目录中寻找 `main.py` |
| `--host 127.0.0.1` | 只监听本机地址 |
| `--port 8000` | 监听 8000 端口 |
| `--reload` | 保存代码后自动重启服务进程 |

## 应用对象

```python
app = FastAPI(
    title="工单系统 API",
    description="Day 74：第一个 FastAPI 应用",
    version="0.1.0"
)
```

`FastAPI(...)` 创建应用对象，`app` 指向该对象。`title`、`description` 和 `version` 会进入 OpenAPI 数据，并显示在自动接口文档中。

## 当前路由

| 方法和路径 | 处理函数 | 结果 |
|---|---|---|
| `GET /` | `get_home()` | 返回服务运行信息 |
| `GET /health` | `get_health()` | 返回 `{"status":"ok"}` |
| `GET /docs` | FastAPI 自动提供 | Swagger UI 接口调试页面 |
| `GET /openapi.json` | FastAPI 自动提供 | 机器可读的 OpenAPI 接口说明 |

`@app.get("/health")` 不会主动访问地址。它在应用启动、模块导入时登记一条规则：以后收到 `GET /health` 请求，就调用 `get_health()`。

```text
启动时：创建函数对象 → 把函数登记到路由表
请求时：匹配方法和路径 → 调用对应函数 → 生成响应
```

## 请求与响应流程

```text
浏览器或 Swagger UI
→ 发送 GET /health
→ Uvicorn 接收请求
→ FastAPI 在 app 中找到 get_health
→ 执行 get_health()
→ 函数返回 Python 字典
→ FastAPI 把字典转换成 JSON
→ Uvicorn 把 HTTP 响应发回客户端
```

`print()` 的内容只显示在服务器终端；路由函数 `return` 的内容才会成为 HTTP 响应。

## 自动重新加载

普通启动时，修改硬盘上的 `main.py` 不会改变已经运行在内存中的应用对象。加入 `--reload` 后，监视进程会在文件保存时停止旧服务进程、创建新服务进程并重新导入代码。

开发模式下可能同时看到监视进程和服务进程，它们分别负责检测文件变化和处理 HTTP 请求。

## 自动文档

- `http://127.0.0.1:8000/docs` 是 Swagger UI，可以直接发送真实 API 请求。
- `http://127.0.0.1:8000/openapi.json` 是 FastAPI 根据应用信息和已登记路由生成的标准接口说明。
- `/docs` 读取 OpenAPI 数据后显示应用标题、版本和路由。

文档中的 `0.1.0` 是当前应用版本；`OAS 3.1` 表示使用 OpenAPI Specification 3.1 标准。

## 实际检查结果

| 请求 | 状态码 | 响应类型或正文 |
|---|---:|---|
| `GET /` | `200` | `application/json`，返回服务信息 |
| `GET /health` | `200` | `application/json`，返回 `{"status":"ok"}` |
| `GET /docs` | `200` | `text/html` |
| `GET /openapi.json` | `200` | `application/json`，包含自定义应用信息和两条业务路由 |
| `GET /missing` | `404` | `{"detail":"Not Found"}` |

`404` 表示请求已经到达运行中的服务器，但没有匹配的路由。停止 Uvicorn 后，8000 端口不再监听，此时客户端无法建立连接，得不到 HTTP 状态码。

## 当前范围

当前服务返回固定 JSON，用来建立应用对象、路由、服务器进程、HTTP 请求和响应之间的完整联系。后续会继续加入路径参数、查询参数、请求正文、工单数据模型和持久化功能。
