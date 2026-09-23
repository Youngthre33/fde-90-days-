# Day 86：使用配置启动工单服务器

## 本节解决什么问题

把端口和日志级别从启动代码中独立出来，让同一份工单代码可以使用不同配置运行。
配置可以来自环境变量或本地 `.env` 文件；缺少配置时使用代码中的默认值。
程序会先检查配置是否合法，再启动服务器。

本节继续使用 Day 82 的工单应用，没有重新实现增删改查。

## 文件分工

| 文件 | 职责 | 是否提交到 Git |
| --- | --- | --- |
| `day86/config.py` | 定义配置字段、默认值、校验规则和读取方式 | 是 |
| `day86/run.py` | 把配置交给 Uvicorn，启动工单服务器 | 是 |
| `day86/.env` | 保存本机实际使用的配置 | 否 |
| `day86/.env.example` | 提供可公开、可复制的配置示例 | 是 |
| `day83/requirements.txt` | 记录本次继续使用的依赖版本 | 是 |

`.gitignore` 中的 `.env` 规则用于忽略实际配置文件，示例文件仍可提交。
示例文件只放可公开的示例值；本地实际配置以后可能包含密码或 API 密钥。

## 配置怎样变成可用的值

```python
model_config = SettingsConfigDict(
    env_prefix="TICKET_",
    env_file="day86/.env",
    env_file_encoding="utf-8",
)
```

- `SettingsConfigDict` 用来组织带类型提示的配置字典；它本身不负责读取环境变量。
- `env_prefix` 让字段 `port` 对应 `TICKET_PORT`，`log_level` 对应 `TICKET_LOG_LEVEL`。
- `env_file` 指定要读取的文件，路径相对于运行命令时的工作目录。
- `env_file_encoding` 指定按 UTF-8 编码读取文件。

执行 `settings = Settings()` 时，`BaseSettings` 提供的机制才会读取配置、转换类型并校验。
例如，文本 `"8001"` 会被转换成整数 `8001`，随后检查端口范围。
不合法的配置会在创建配置对象时抛出校验错误，因此服务器不会继续启动。

| 字段 | 默认值 | 允许的值 |
| --- | --- | --- |
| `port` | `8000` | 大于等于 1、小于等于 65535 的整数 |
| `log_level` | `"info"` | `debug`、`info`、`warning`、`error` |

当前使用 `Settings()`，没有传入构造参数。对同一个字段，本节取值顺序为：

```text
终端环境变量 > .env 文件 > 代码中的默认值
```

例如，代码默认端口为 8000、文件写 8001、终端设置 8002，最终得到 8002。
读取 `.env` 是配置库的功能；单独创建这个文件不会让 PowerShell 自动设置环境变量。

## 准备环境与配置

所有命令都在仓库根目录 `fde-90-days-` 中运行，使用 PowerShell。
已有虚拟环境和依赖的电脑可以跳过下面的环境创建与安装命令。

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r day83/requirements.txt
```

本节继续复用 Day 83 的依赖快照，没有新增依赖或重复创建另一份清单。
其中已包含 `pydantic-settings`、`python-dotenv` 和 `uvicorn`。
显式使用虚拟环境中的 Python 路径，不要求先激活虚拟环境。

首次使用且尚无本地 `.env` 时，复制示例文件：

```powershell
if (-not (Test-Path day86/.env)) {
    Copy-Item day86/.env.example day86/.env
}
```

示例配置内容：

```dotenv
TICKET_PORT=8001
TICKET_LOG_LEVEL=debug
```

## 启动服务器

清除之前练习留下的同名环境变量，让程序使用 `.env` 中的值，然后启动：

```powershell
Remove-Item Env:TICKET_PORT, Env:TICKET_LOG_LEVEL -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe -m day86.run
```

浏览器访问 `http://127.0.0.1:8001/health`，正常时返回 `{"status":"ok"}`。
访问 `http://127.0.0.1:8001/docs` 可以查看并操作工单接口。
终端持续运行是正常现象；在这个终端按 `Ctrl + C` 停止服务器。

启动代码中的 `if __name__ == "__main__":` 判断当前模块是否作为程序入口运行。
运行 `python -m day86.run` 时会启动服务器，其他代码仅导入该模块时不会启动。
`uvicorn.run(...)` 是函数调用，它启动监听请求的服务器。
字符串 `"day82.main:app"` 指定模块 `day82.main` 中的 `app` 对象。
其中的冒号是 Uvicorn 约定的分隔符，并不是因为 Python 的点号不能重复使用。

实际应用来自 Day 82，所以 `/docs` 中仍显示 Day 82 的介绍是正常的。
工单仍保存在应用进程的内存中，重新启动后会重新加载代码中的初始数据。
修改 `.env` 后需要重新启动，新的 `Settings()` 才会重新读取配置。

## 建议一次完成的验证

下面把配置读取、环境覆盖和 Git 忽略检查放在一起。
运行检查配置的命令前，先停止占用当前终端的服务器。

```powershell
Remove-Item Env:TICKET_PORT, Env:TICKET_LOG_LEVEL -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe -c "from day86.config import settings; print(settings.model_dump())"
$env:TICKET_PORT = "8002"
.\.venv\Scripts\python.exe -c "from day86.config import settings; print(settings.model_dump())"
Remove-Item Env:TICKET_PORT -ErrorAction SilentlyContinue
git check-ignore -v day86/.env day86/.env.example
```

| 检查 | 预期结果 |
| --- | --- |
| 清理环境变量后打印配置 | `{'port': 8001, 'log_level': 'debug'}` |
| 设置 `TICKET_PORT=8002` 后打印配置 | 端口变为 8002，日志级别仍为 debug |
| Git 忽略检查 | 只列出 `.env` 被忽略的记录，不列出 `.env.example` |
| 清除临时端口后重新启动并访问 `/health` | 在 8001 启动并返回 `{"status":"ok"}` |

本节完整流程：配置来源 → `Settings()` 读取与校验 → `settings` 对象 → `uvicorn.run(...)` → 工单应用处理请求。
