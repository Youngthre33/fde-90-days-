# Day84：隔离会修改工单数据的业务测试

## 本节解决的问题

创建、修改和删除会改变共享内存列表。如果测试直接继承前一个测试留下的数据，结果就可能依赖执行顺序。本节使用 fixture 为每个测试准备固定数据，测试结束后恢复原数据内容。

测试仍直接调用 Day82 的业务函数，不需要启动 Uvicorn 或打开 Swagger。

## 文件与依赖

- `test_ticket_mutations.py`：一个自动使用的 fixture 和五个业务测试。
- `../day82/ticket_service.py`：被测试的创建、查询、修改和删除函数。
- `../day82/ticket_store.py`：创建 service 与测试共同引用的列表。
- `../day83/requirements.txt`：继续使用上一节包含 pytest 的环境依赖快照；本节没有新增依赖。

## 运行

在仓库根目录执行，按需要选择单独运行本节或合并运行两节：

```powershell
.\.venv\Scripts\python.exe -m pytest day84/test_ticket_mutations.py -v
.\.venv\Scripts\python.exe -m pytest day83/test_ticket_service.py day84/test_ticket_mutations.py -v
```

预期分别为 `5 passed` 和 `9 passed`。这些数字表示测试函数数量，不表示断言总数或所有功能都已覆盖。

如需在新建的虚拟环境中安装依赖，可在仓库根目录执行：

```powershell
.\.venv\Scripts\python.exe -m pip install -r day83/requirements.txt
```

## fixture 的执行流程

```text
pytest 准备运行当前测试
  → deepcopy(tickets) 备份数据内容
  → tickets[:] = [...] 放入四张固定工单
  → 到达 yield，暂停 fixture
  → 执行当前测试函数
  → 测试结束后，从 yield 后继续
  → tickets[:] = original_tickets 恢复数据内容
```

`@pytest.fixture(autouse=True)` 让当前模块中的测试自动使用该 fixture。默认作用范围是单个测试函数，所以每个测试都会分别准备和恢复数据。测试中的断言失败后，pytest 仍会执行这里的恢复部分。

fixture 的恢复不是无条件保证：如果准备阶段在到达 `yield` 前就失败，pytest 不会执行该 fixture 的 `yield` 后代码。

## 关键语法和设计

- `tickets = 新列表` 重新绑定名称，不能自动改变其他模块中名称的指向。
- `tickets[:] = 新列表` 保留共享列表对象，替换它的全部元素。
- `new_tickets = tickets[:]` 是读取切片，创建新的外层列表；这与切片赋值不同。
- `deepcopy(tickets)` 创建独立的数据备份，包括列表内的字典。恢复的是数据内容，不保证恢复旧字典的对象身份。
- `yield` 在这里是由 pytest 管理的暂停点，分开测试前的准备和测试后的恢复；它不是 `return`。
- 四张工单只是测试选定的已知起点。也可以准备五张，但数量和新 ID 的预期应相应调整。
- 在测试中另建一个列表，业务函数不会自动改用它。当前 service 固定引用 store 中的共享列表；如果改为由调用者传入列表，测试就可以使用独立列表，这是另一种设计。

## 五个测试检查什么

| 测试 | 操作与预期 |
|---|---|
| 创建 | 创建 105，默认 open，列表变成五张，查回同一个对象 |
| 修改 | 修改 101 为 done，保留 ID、标题和原对象身份 |
| 删除 | 删除 103，返回被删对象，列表变成三张，再次查找得到 None |
| 修改不存在的 ID | 返回 None，列表数据内容不变 |
| 删除不存在的 ID | 返回 None，列表数据内容不变 |

`is` 检查是否同一个对象，`==` 检查值或内容是否相等。修改前保存 `original_ticket`，才能比较修改前后的对象身份；修改后再查找，只能比较返回对象与列表中当前的对象。

`original_ticket = find_ticket_by_id(101)` 只保留对象引用，不复制字典，也不会固定修改前的字段值。

## 本节结果与下一步

学习者亲手完成 fixture 和五个测试，运行 Day83 与 Day84 合集得到 `9 passed`。课程收尾整理变量拼写和格式，不改变业务逻辑。

本节覆盖业务函数及共享数据变化，尚未验证路由、HTTP 状态码、请求参数校验和响应模型。下一节使用 TestClient 检查 FastAPI 接口层。
