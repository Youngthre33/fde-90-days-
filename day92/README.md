# Day 92：工单系统运行与接口使用说明

## 本节目标

让拿到代码的开发者或交付伙伴，能根据说明安装依赖、配置端口、启动服务并找到接口示例。
Day89—91 已完成网页与 Python 后端的查询、创建、修改、删除；Day92 整理运行资料，Day93 按说明完成阶段演示，Day94 起学习数据库。

当前是一套本机学习版本：普通用户使用网页，开发者负责安装和启动。尚未部署为客户通过公网访问的服务。

## 使用哪一份程序

必须取得完整仓库，不能只复制 day92 文件夹。

| 位置 | 用途 |
| --- | --- |
| `day91/index.html` 和同目录 JavaScript | 当前网页界面，由浏览器运行 |
| `day90/main.py`、`ticket_service.py`、`run.py` | 当前后端入口、业务处理和启动代码 |
| `day86/config.py`、`.env.example` | 配置读取规则与可提交的配置示例 |
| `day82/ticket_store.py` | 后端启动时使用的初始工单 |
| `day92/requirements.txt` | 本节生成的 Python 包与版本清单 |
| `day92/API_EXAMPLES.md` | 请求方法、路径、输入、输出和错误示例 |

Day92 没有新的 `run.py` 或 `index.html`，继续运行 Day90 后端和 Day91 网页。

## 当前开发者：生成依赖清单

在仓库根目录、一个没有被服务器占用的 PowerShell 终端执行：

```powershell
.\.venv\Scripts\python.exe -m pip freeze | Set-Content -Encoding utf8 .\day92\requirements.txt
```

这一步由学习者执行并将生成的文件一起提交。`pip freeze` 列出当前虚拟环境安装的包与版本，竖线将输出交给 `Set-Content` 保存。
它记录实际安装情况，不分析哪些包是项目的最小必需项，也不是跨平台安装保证。[pip freeze 官方说明](https://pip.pypa.io/en/stable/cli/pip_freeze/)

此项目的主要包包括 FastAPI、Uvicorn、Pydantic、pydantic-settings、pytest 和 HTTPX；清单中还会包含这些包需要的其他包。
后续新增依赖时再更新清单；不要用另一项目或全局 Python 的环境生成本项目清单。

## 新电脑：首次准备

以下面向 Windows PowerShell，先安装 Git 和 Python 3.12，并确认 `py -3.12 --version` 能运行。当前课堂环境为 Python 3.12.5。
在准备存放项目的位置执行；已有完整仓库时，直接进入仓库根目录：

```powershell
git clone https://github.com/Youngthre33/fde-90-days-.git
cd fde-90-days-
```

新电脑第一次安装，在仓库根目录执行：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\day92\requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

`install -r` 按清单安装，安装过程需要能访问包源；`pip check` 核对已安装包之间的依赖要求，正常输出 `No broken requirements found.`。
已有能工作的 `.venv` 不用重新创建。虚拟环境应在目标电脑重建，不直接复制旧电脑的 `.venv`；上面的命令指定解释器路径，因此不依赖先执行激活脚本。[Python venv 官方说明](https://docs.python.org/3.12/library/venv.html)

## 准备配置

在仓库根目录执行。只有本地文件不存在时才从示例创建，已有配置会保留：

```powershell
if (-not (Test-Path -LiteralPath .\day86\.env)) {
    Copy-Item -LiteralPath .\day86\.env.example -Destination .\day86\.env
}
```

当前配置示例为：

```dotenv
TICKET_PORT=8001
TICKET_LOG_LEVEL=debug
```

`.env.example` 是给别人参考并纳入 Git 的模板；`.env` 是这台电脑使用的配置，已被 `.gitignore` 忽略。
配置代码读的是 `day86/.env`，不是 `day92/.env`。漏掉该文件且未设置环境变量时，代码默认端口为 8000，而当前网页请求 8001，因此两边无法对应。
终端中的同名环境变量可以覆盖文件配置，以后端实际启动日志为准。当前按示例保持 8001；改变后端端口时也要调整前端 API 地址。

## 启动两个服务

两个 PowerShell 终端都要位于仓库根目录，即能看到 `day90`、`day91` 等目录的位置。
已在运行的相同服务无需再启动；需要重启时，在对应终端按 Ctrl+C 后再执行命令。后端重启会丢失尚未持久化的练习改动。

终端一：启动处理工单的 Python 后端。

```powershell
.\.venv\Scripts\python.exe -m day90.run
```

日志应显示 `Uvicorn running on http://127.0.0.1:8001`。终端保留运行，用于查看请求日志。

终端二：启动提供网页文件的服务。

```powershell
.\.venv\Scripts\python.exe -m http.server 5500 --bind 127.0.0.1
```

日志应显示服务使用 5500。它把 HTML 和 JavaScript 交给浏览器；浏览器执行 JavaScript 后，直接请求 8001 后端。

| 在浏览器打开 | 用途 | 应看到什么 |
| --- | --- | --- |
| [网页界面](http://127.0.0.1:5500/day91/index.html) | 用户操作工单 | 列表以及新增、编辑、状态、删除按钮 |
| [健康检查](http://127.0.0.1:8001/health) | 检查后端是否能回复 | `{"status":"ok"}` |
| [Swagger 接口说明](http://127.0.0.1:8001/docs) | 开发者查看和尝试接口 | GET、POST、PATCH、DELETE 等条目 |

`127.0.0.1` 指访问者自己的电脑。请按这里的地址使用 `127.0.0.1`，不要替换成 `localhost`；当前跨来源配置只允许 `http://127.0.0.1:5500`。

## 接口示例与现有测试

完整请求、回复及错误示例见 [API_EXAMPLES.md](API_EXAMPLES.md)。Swagger 的操作顺序是：展开条目 → Try it out → 输入参数或 JSON → Execute → 查看 Server response。

以下是已有历史版本的 Python 自动测试，可在空闲终端从仓库根目录运行：

```powershell
.\.venv\Scripts\python.exe -m pytest day83/test_ticket_service.py day84/test_ticket_mutations.py day85/test_ticket_api.py -v
```

目前共有 19 个测试。Day83、84 检查 Day82 业务函数，Day85 用 TestClient 检查 Day82 应用；测试在自己的进程中运行，不连接 8001，也不会修改正在运行的后端内存。
这些旧测试不覆盖当前 Day90 的启动、日志与 CORS，或 Day91 浏览器交互。当前网页功能还需要实际浏览器操作核对，不能用旧测试通过代替全部验证。
Day93的本次阶段验收复用Day85的10项接口测试，将app导入改为当前Day90应用；具体准备、命令及网页核对见 [Day93阶段验收](../day93/README.md)。

## 常见问题：先看哪里

| 现象 | 优先检查 |
| --- | --- |
| Python 报找不到 day90 模块 | 终端是否在仓库根目录，是否使用 `-m day90.run` |
| 报找不到 fastapi、pydantic_settings 等包 | 是否完成清单安装，并使用 `.venv\Scripts\python.exe` |
| 后端日志显示 8000，网页请求失败 | `day86/.env` 是否存在，端口是否为8001，终端环境变量是否覆盖 |
| 打开5500看到文件目录 | 地址中补齐 `/day91/index.html` |
| 网页无法加载工单 | 先开8001的 `/health`，再看后端日志和浏览器 F12 → Console／Network |
| 浏览器显示 CORS 错误 | 网页来源是否为127.0.0.1:5500；也检查是否伴随500，先修后端实际异常 |
| 报端口被占用 | 是否重复启动同一服务；返回原终端确认进程，不要盲目反复换端口 |
| 返回422 | 查看回复的detail，检查标题是否为空、状态是否为允许值、编号是否为正整数 |
| 返回404 | 分清路径写错与工单不存在；核对实际工单编号 |
| 返回500 | 到后端终端查看错误追踪，不能仅凭页面提示确定原因 |

## 当前范围与验证记录

- 所有工单变化仍在后端内存中；刷新网页会重新读取，重启后端会恢复初始记录。
- 本机版本尚无登录和权限控制，不能直接视作完成生产部署；后续按课程推进数据库、安全和部署。
- 当前仅拒绝空字符串标题，不会去掉首尾空格；删除成功为204空正文，不应再对其调用 `response.json()`。
- 编写本说明时已核对实际路径、入口、配置示例、包版本和接口定义，并在已有课堂环境执行 `pip check` 通过。
- 未进行新电脑或全新虚拟环境的安装验证，也未重新执行19个旧测试。学习者已生成依赖清单并随Day92提交推送，提交为ac57040；后续实际启动和网页整体验收按Day93进行。
