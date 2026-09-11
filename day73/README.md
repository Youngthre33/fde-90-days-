# Day73：Python 虚拟环境和项目依赖

## 今天为什么学这些

Day72 解决了“程序运行后怎样成为监听端口的服务器进程”。Day73 继续解决三个问题：由哪个 Python 执行代码、第三方包被安装到哪里，以及其他电脑怎样重建相同的项目环境。

后端项目将使用 FastAPI 和 Uvicorn。它们不属于 Python 标准库，必须作为项目依赖安装。

## 关键角色

| 名称 | 作用 |
|---|---|
| Python 解释器 | 读取并执行 `.py` 文件的 `python.exe` |
| 标准库 | Python 自带的模块，例如 `sys`、`venv`、`http.server` |
| 第三方包 | 另外安装的代码，例如 FastAPI 和 Uvicorn |
| pip | 给指定 Python 环境安装和管理第三方包 |
| `.venv` | 当前项目专用的解释器入口、配置和第三方包目录 |
| `requirements.txt` | 记录可用于重建环境的包名和确切版本 |

`.venv` 是文件夹，不是服务器进程，不会监听端口。`pip install` 只把文件安装到环境中，也不会自动启动服务器。

## 为什么使用虚拟环境

如果所有项目都共用全局 `site-packages`，一个项目升级或降级某个包时，可能破坏另一个项目。

```text
项目 A 的 .venv → 包 1.0
项目 B 的 .venv → 包 2.0
```

两个项目的依赖因此可以互不干扰。虚拟环境还可以随时删除，再根据依赖清单重建。

## 当前电脑上的两套环境

全局环境：

```text
Python 3.14.6
C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe
C:\Users\Administrator\AppData\Local\Programs\Python\Python314\Lib\site-packages
```

项目虚拟环境：

```text
Python 3.12.5
C:\Users\Administrator\Documents\GitHub\fde-90-days-\.venv\Scripts\python.exe
C:\Users\Administrator\Documents\GitHub\fde-90-days-\.venv\Lib\site-packages
```

使用 Python 3.12 创建 `.venv` 没有降低或修改全局 Python 3.14。它只是选用电脑上已经安装的 Python 3.12 作为当前项目环境的基础。

## 创建项目环境

仓库根目录的 `.gitignore` 包含：

```gitignore
.venv/
__pycache__/
*.pyc
/test.js
```

然后创建环境：

```powershell
py -3.12 -m venv .venv
```

命令含义：

| 部分 | 含义 |
|---|---|
| `py` | Windows Python 启动器 |
| `-3.12` | 明确选择已经安装的 Python 3.12 |
| `-m venv` | 运行 Python 自带的虚拟环境模块 |
| `.venv` | 要创建的项目环境目录 |

## 不激活也可以使用虚拟环境

当前 PowerShell 会阻止部分 `.ps1` 脚本，因此没有依赖 `Activate.ps1`，也没有修改系统执行策略。直接指定环境中的解释器即可：

```powershell
.\.venv\Scripts\python.exe --version
```

```powershell
.\.venv\Scripts\python.exe -m pip --version
```

“激活虚拟环境”主要是在当前终端中调整 `PATH`，让简短的 `python` 自动指向 `.venv`。激活不会创建服务器进程；不激活也不影响通过完整路径使用环境。

## 为什么使用 `python -m pip`

```powershell
.\.venv\Scripts\python.exe -m pip install "fastapi[standard]"
```

这条命令明确表示：让 `.venv` 中的 Python 运行它自己的 pip，并把包安装到 `.venv\Lib\site-packages`。

只写裸 `pip` 时，电脑上存在多个 Python 的情况下可能难以立即判断它属于哪个解释器。

## 依赖隔离实验

安装前，两套解释器都无法导入 FastAPI：

```powershell
python -c "import fastapi"
.\.venv\Scripts\python.exe -c "import fastapi"
```

两者都返回：

```text
ModuleNotFoundError: No module named 'fastapi'
```

只在 `.venv` 中安装：

```powershell
.\.venv\Scripts\python.exe -m pip install "fastapi[standard]"
```

安装后：

```text
全局 Python 3.14 → 仍然无法导入 FastAPI
.venv Python 3.12 → 能导入 FastAPI 0.141.1 和 Uvicorn 0.52.4
```

这证明包是否可用取决于执行代码的解释器及其模块搜索路径。

## 环境诊断程序

运行：

```powershell
.\.venv\Scripts\python.exe day73\environment_info.py
```

程序使用：

- `sys.executable` 显示当前解释器路径；
- `sys.version` 显示 Python 版本；
- `fastapi.__version__` 和 `uvicorn.__version__` 显示包版本；
- `fastapi.__file__` 显示包实际加载位置。

同一个 Python 文件由不同解释器执行时，可以得到不同的导入结果。遇到“明明安装了包却无法导入”时，首先检查 `sys.executable` 和 `pip --version` 的路径。

## 直接依赖和间接依赖

主动安装的是直接依赖：

```text
fastapi[standard]
```

FastAPI 正常工作还需要其他包。例如本次安装关系的一部分是：

```text
FastAPI → annotated-doc、Pydantic、Starlette、typing-extensions、typing-inspection
Uvicorn → click、h11
```

这些由直接依赖继续需要的包叫间接依赖或传递依赖。因此只输入一个安装目标，pip 最终安装了多项内容。

## 生成依赖清单

```powershell
.\.venv\Scripts\python.exe -m pip freeze > day73\requirements.txt
```

- `pip freeze` 打印当前环境中已安装的包和确切版本。
- `>` 是 PowerShell 输出重定向符号，把终端输出写入文件。
- 单个 `>` 会覆盖目标文件原来的内容。

本次 `requirements.txt` 记录了 44 个直接或间接依赖。它保存的是包名和版本，不包含包的源代码。

## 为什么提交 requirements 而不提交 .venv

| `.venv` | `requirements.txt` |
|---|---|
| 当前电脑实际生成的环境 | 重建环境的文字清单 |
| 文件多且包含本机路径 | 文件小且适合代码审查 |
| Windows、macOS、Linux 内容可能不同 | pip 可以在目标系统重新解析和安装 |
| 添加到 `.gitignore` | 提交到 Git |

重建命令：

```powershell
python -m pip install -r day73\requirements.txt
```

其中 `-r` 表示从指定 requirements 文件读取安装要求。

## 实际重建验证

本课在系统临时目录创建了一套全新的 Python 3.12 虚拟环境，只执行：

```powershell
python -m pip install -r day73\requirements.txt
```

验证结果：

```text
FastAPI 0.141.1 导入成功
Uvicorn 0.52.4 导入成功
No broken requirements found.
```

验证结束后临时环境已删除。这证明当前依赖清单能够从空环境重建相同版本。

## 与 Day72 和 Day74 的连接

```text
Day72
程序运行 → 产生进程 → 监听端口

Day73
选择解释器 → 隔离环境 → 安装并记录依赖

Day74
编写 FastAPI 路由 → 启动 Uvicorn → 产生服务器进程 → 监听 8000
```

FastAPI 将负责声明路由和组织 API 行为；Uvicorn 将负责运行应用、监听端口和接收 HTTP 请求。

## Day73 验收标准

- 能区分解释器、标准库、第三方包、pip、虚拟环境和依赖清单。
- 能说明虚拟环境的主要目的不是降低 Python 版本，而是隔离项目依赖。
- 能根据解释器和 pip 的路径判断包会安装到哪里。
- 能说明 `.venv` 不监听端口，安装 FastAPI 也不会自动启动服务器。
- 能区分直接依赖和间接依赖。
- 能解释为什么 `.venv` 不提交，而 `requirements.txt` 应提交。
- 能使用依赖清单重建一套可用环境。
