# Day83：用 pytest 检查工单业务函数

## 本节目标

把对业务函数的检查保存为可以重复运行的测试。调用 Day82 已有的 service 函数，通过 `assert` 比较实际结果与预期结果；以后修改代码时，可以重新运行这些测试，检查已覆盖的行为是否仍然成立。

## 文件与分工

- `test_ticket_service.py`：四个只读业务测试。
- `requirements.txt`：包含 pytest 的当前虚拟环境依赖快照。
- `../day82/ticket_service.py`：被测试的业务函数。
- `../day82/ticket_store.py`：测试进程导入时加载的初始工单列表。

本节直接导入 Day82，不复制应用。测试文件与 Day82 模块需要保留在同一仓库中。

## 安装与运行

以下命令均在仓库根目录执行，使用项目虚拟环境中的 Python：

```powershell
.\.venv\Scripts\python.exe -m pip install -r day83/requirements.txt
.\.venv\Scripts\python.exe -m pytest day83/test_ticket_service.py -v
```

不需要启动 Uvicorn 或打开 Swagger。pytest 在自己的 Python 进程中调用业务函数，不访问正在运行的 HTTP 服务，也不读取该服务进程中通过 Swagger 修改的数据。

## 四个测试

| 测试 | 预期行为 |
|---|---|
| `test_find_existing_ticket` | 查找 101，得到 ID、标题和状态正确的工单 |
| `test_find_missing_ticket` | 查找 999，得到 `None` |
| `test_list_open_tickets` | 筛选 open，得到 101、103 |
| `test_list_tickets_with_limit` | 不筛选状态，限制两条，得到 101、102 |

恢复正确断言后的预期汇总为 `4 passed`。这代表四个测试函数通过，不表示只有四条断言，也不证明所有功能都已被测试。

## 执行流程

```text
终端运行 pytest
  → 发现并调用 test_ 开头的测试函数
  → 测试函数调用 service
  → service 读取 store 并返回结果
  → assert 检查结果
  → pytest 汇总通过或失败
```

`assert` 是 Python 语句，不需要 `import pytest` 才能使用。条件为真时继续执行；条件为假时抛出 `AssertionError`，本测试函数后面的语句不会继续执行。默认情况下，pytest 仍会继续运行其他测试。

## 故意失败实验

保持 `find_ticket_by_id(101)` 不变，把第一个测试中的 ID 断言临时改成 `assert ticket["id"] == 999`。实际 ID 为 101，预期写成 999，因此出现 `assert 101 == 999` 和 `1 failed, 3 passed`。

实验结束后应恢复成 `assert ticket["id"] == 101`，保存并重新运行同一条命令，确认 `4 passed` 后再提交。

## 当前范围与后续

本节只读取返回结果，没有增删或修改共享数据。返回的工单字典仍可能是 store 中的原对象，所以测试中不要直接给字典字段赋值。

本节尚未覆盖 HTTP 路由、请求校验、状态码以及创建、修改、删除业务。Day84 再学习 fixture，为会修改共享列表的测试准备并恢复数据；接口层测试后续单独进行。
