# Day 88：让网页读取 Python 后端的数据

## 今天解决什么问题，和后面几天怎么连接

真实客户会在网页上点击查询、创建、删除。网页需要把请求发给后端，再把后端返回的数据展示出来。
目前网页来自 `http://127.0.0.1:5500`，Python 后端位于 `http://127.0.0.1:8001`，两者端口不同。
本节配置 CORS（跨来源资源共享），让浏览器允许这个网页里的 JavaScript 读取后端回复。

| 课程 | 本节在完整功能中的位置 | 客户最终能做什么 |
| --- | --- | --- |
| Day 88 | 打通网页跨来源读取后端数据的通路 | 为正式网页操作准备连接条件 |
| Day 89 | 复用 Day 71 网页，读取并显示 Python 后端工单 | 打开网页就能看到工单列表 |
| Day 90 | 接通网页创建、删除操作和 Python 后端 | 在网页提交问题或删除记录，并看到结果 |

这些步骤合起来，实现“客户操作网页 → 后端处理工单 → 网页展示结果”。Day 88 尚未接好正式工单页面。

## 谁在运行，谁给谁发请求

| 当前角色 | 实际负责的事情 | 真实使用时的对应角色 |
| --- | --- | --- |
| 浏览器 | 显示网页、运行 JavaScript、发送请求 | 客户使用系统的工具 |
| 5500 的文件服务 | 把 HTML、CSS、JavaScript 文件交给浏览器 | 部署后提供网页文件的服务 |
| 8001 的 Python 后端 | 查询、创建、修改、删除工单（一条问题记录） | 部署后处理客户业务的服务 |
| 两个终端 | 启动这两个程序、查看输出 | 开发者的操作窗口，客户通常不用打开 |

```text
浏览器向 5500 要网页文件 → 5500 返回文件 → 浏览器显示网页并运行 JavaScript
浏览器里的 JavaScript 向 8001 要工单 → Python 后端返回数据 → 浏览器更新页面
```

第二行请求由浏览器直接发给后端，5500 不负责转发。
`127.0.0.1` 表示访问者自己的设备；5500、8001 是本次开发选择的入口编号，不是固定的前后端标准端口。
现在两个服务都运行在自己的电脑上，后续部署才会改为供客户访问的地址。

## 启动两个服务

在仓库根目录 `fde-90-days-` 打开两个 PowerShell 终端。
第一个启动处理工单的后端：

```powershell
.\.venv\Scripts\python.exe -m day88.run
```

端口继续读取 Day 86 配置，当前练习使用 8001；以启动日志显示的地址为准。
配置读取 `day86/.env`，同名环境变量可以覆盖它。修改代码后按 `Ctrl+C` 停止，再运行上述命令加载新代码。
第二个启动提供网页文件的服务：

```powershell
.\.venv\Scripts\python.exe -m http.server 5500 --bind 127.0.0.1
```

打开 `http://127.0.0.1:5500/`，出现目录页是本节的预期结果；暂时借这个页面做实验。
`http://127.0.0.1:8001/docs` 是 Swagger 接口测试页，来自后端自身地址，不适合证明 5500 网页的跨来源读取成功。

## 后端的 CORS 配置

`main.py` 导入 `CORSMiddleware`，在创建 `app` 后、登记日志中间件前添加：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
    expose_headers=["X-Request-ID"],
)
```

- `allow_origins`：允许哪些来源的网页读取回复；来源由协议、主机、端口组成，不带路径。
- `allow_methods`：允许跨来源请求使用哪些操作方式。
- `allow_headers`：允许请求携带哪些自定义或非简单请求头；这里需要发送 JSON 的 `Content-Type`。
- `expose_headers`：允许网页 JavaScript 读取回复里的 `X-Request-ID`；编号仍由 Day 87 的日志中间件生成。

`localhost` 与 `127.0.0.1` 是不同主机名，配置与页面实际地址必须对应。
日志中间件在 CORS 之后登记，所以普通请求及 CORS 处理的 OPTIONS 预检也会经过日志步骤。
“预检”是浏览器在发送某些请求前先询问后端是否允许，CORS 组件自动处理，无需另写 OPTIONS 路由。

## 一次完成浏览器核对

保持两个服务运行。先直接打开 `http://127.0.0.1:8001/health`，确认显示 `{"status":"ok"}`。
再回到 `http://127.0.0.1:5500/`，刷新页面，按 F12 打开 Console（控制台），执行：

```javascript
const response = await fetch("http://127.0.0.1:8001/health");
console.log(response.status, await response.json());
console.log(response.headers.get("X-Request-ID"));
```

预期看到 `200`、`{status: "ok"}` 和一串 32 位十六进制请求编号。
直接访问后端成功只说明后端能回应；在 5500 页面读取成功，才证明本次网页跨来源读取可用。
同一个页面反复声明 `const response` 可能报重复声明；刷新页面后再执行即可。
助手已用 Chrome 打开实际 5500 页面并执行上述跨来源请求，确认能读取 200、JSON 和请求编号；这属于助手验证，不代替学习者本人操作的记录。

## 本次排错与当前边界

本次曾把 `expose_headers` 拼成 `expected_headers`，导致 CORS 组件不接受参数，后端返回 500。
错误回复缺少跨来源许可时，浏览器还会同时显示 CORS 错误。因此看见 CORS 提示也要检查状态码及后端终端日志。
参数名修正后需要重启后端加载修改；本次后续核对确认正在运行的服务已经正常回应。

正常回复缺少 CORS 许可时，后端也可能已经处理并返回 200，只是浏览器不允许网页 JavaScript 读取。
CORS 配合浏览器管理跨来源读取，不代替登录和工单访问权限判断。
当前中间件安排下，未处理异常生成的 500 回复可能仍缺少 CORS 许可和请求编号；详细追踪信息在后端终端。
业务继续复用 Day 82 的内存列表，重启会恢复初始工单；本节没有增加数据库、依赖或自动化测试文件。

## 参考

- [FastAPI：CORS](https://fastapi.tiangolo.com/tutorial/cors/)
- [Starlette：CORS 中间件及异常回复的全局处理](https://starlette.dev/middleware/#corsmiddleware-global-enforcement)
