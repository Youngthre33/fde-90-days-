# Day96：在数据库中新增、修改、删除工单

## 实际用途和课程位置

客户提交问题、客服改标题或处理状态、删除误建记录，都需要改变保存的数据。Day94建表，Day95查询，今天补齐INSERT／UPDATE／DELETE。Day97学习数据约束，Day98让Python连接数据库，Day99把后端的内存存储换成数据库存储，合起来实现重启后仍保留工单的完整功能。

今天由学习者在终端直接操作本机SQLite文件；客户将来在网页点击，由Python后端执行相应数据库操作。当前网页和后端仍未连接这些练习数据库，不需要启动5500或8001来完成本节。

## 独立练习数据

使用day96/tickets.db，表结构来自day94/schema.sql，六条样本来自day95/seed.sql。初始id为101—106，状态分别为open、in_progress、open、done、open、done。本次只新增、修改、删除107，原六条样本用于观察其他记录保持原样。

教师已准备当前电脑上的数据库时，不重复初始化。以下命令仅用于文件尚不存在时，在仓库根目录PowerShell首次重建练习环境：

```powershell
if (Test-Path -LiteralPath .\day96\tickets.db) { throw 'Database already exists; stop initialization.' }
.\.venv\Scripts\python.exe -m sqlite3 .\day96\tickets.db (Get-Content -LiteralPath .\day94\schema.sql -Raw -Encoding utf8)
if ($LASTEXITCODE -ne 0) { throw 'Schema initialization failed.' }
.\.venv\Scripts\python.exe -m sqlite3 .\day96\tickets.db (Get-Content -LiteralPath .\day95\seed.sql -Raw -Encoding utf8)
if ($LASTEXITCODE -ne 0) { throw 'Seed initialization failed.' }
```

本目录.gitignore忽略本地数据库文件；提交SQL与说明。不要通过删库来重复练习。

## 打开操作入口

在day96中新建writes.sql，亲手保存下方各条SQL。文件只保存SQL，不把.quit或PowerShell命令写进去。保存文件不会执行；本节逐条选中完整语句（含分号），粘贴到sqlite>并按Enter。按顺序首次执行，不在流程中重复INSERT同一个107。

在仓库根目录PowerShell执行：

```powershell
.\.venv\Scripts\python.exe -X utf8 -m sqlite3 .\day96\tickets.db
```

出现sqlite>后输入SQL。未输入分号时的...表示等待该条指令结束。退出工具输入.quit并按Enter。

## 连贯操作

### 1. 新增107

```sql
INSERT INTO tickets (id, title, status)
VALUES (107, 'Day96：客户无法登录', 'open');

SELECT id, title, status
FROM tickets
WHERE id = 107;
```

每次执行一条。INSERT INTO指定放入哪张表，括号列出要填的列，VALUES按同一顺序提供各列的值。本例明确提供status；当前数据库表没有给status设置默认值，后端创建时默认open的Python逻辑不会在这里自动执行。107是本次手写且尚未占用的编号。

### 2. 修改同一条107

```sql
UPDATE tickets
SET title = 'Day96：登录问题已确认',
    status = 'in_progress'
WHERE id = 107;

SELECT id, title, status
FROM tickets
WHERE id = 107;
```

UPDATE指定修改哪张表。WHERE id = 107筛选要改的行；SET指定这些行中哪些列改成什么值，逗号隔开两项修改。id未在SET中出现，保持107。SET中的等号指定新值，WHERE中的等号比较是否相等。不是向表中再加一条。

### 3. 退出，再打开同一文件查询

先在sqlite>输入.quit。回到PowerShell后再次执行上面的打开命令，再执行一次WHERE id = 107的SELECT。预期仍是修改后的标题和in_progress。

本机Python3.12的sqlite3命令行工具会自动提交本节这些独立写操作。退出重开仍能查到，说明数据已经保存在day96/tickets.db；不是靠终端界面记住它。以后自己写Python连接代码时再学习提交与事务，不把这个行为推广成所有Python数据库代码都自动保存。

### 4. 删除107，查看剩余记录

```sql
DELETE FROM tickets
WHERE id = 107;

SELECT id, title, status
FROM tickets
ORDER BY id;
```

DELETE FROM指定从哪张表删除记录，WHERE确定范围。这里删除107的整行，表结构仍在。最后按id升序显示原来的101—106六条样本，不再有107。检查后输入.quit退出。

## 一次核对结果

| 操作后执行查询 | 预期 |
| --- | --- |
| 新增107后查询107 | (107, 'Day96：客户无法登录', 'open') |
| 修改107后查询107 | (107, 'Day96：登录问题已确认', 'in_progress') |
| 退出、重开同一个文件再查107 | 仍为修改后的内容 |
| 删除107后查询全部，按id升序 | 101、102、103、104、105、106，原内容不变 |

本例写操作执行后没有显示一行工单是正常的，SELECT用来读取结果并显示。首次按上述顺序操作时，新增／修改／删除各影响一行；主键唯一使WHERE id = 107最多匹配一行，若该编号不存在则UPDATE／DELETE影响零行。

## 整块流程回顾

```text
你在终端输入一条SQL
  → SQLite读取指令
  → 对day96/tickets.db中的tickets表新增／修改／删除记录
  → 这次命令行工具自动提交写入
  → 你再执行SELECT
  → 终端显示数据库中目前的结果
```

INSERT增行；UPDATE改已有行的列值；DELETE删行；SELECT读当前记录。UPDATE／DELETE中的WHERE决定涉及哪些记录；省略WHERE会涉及表中所有记录，不会默认只处理当前看到的一条。参考：[INSERT](https://www.sqlite.org/lang_insert.html)、[UPDATE](https://www.sqlite.org/lang_update.html)、[DELETE](https://www.sqlite.org/lang_delete.html)。

## 完成整块后，两道关键理解题

只预测，不执行这些变体。

1. 在UPDATE tickets SET status = 'in_progress' WHERE id = 107;中，两个等号分别在做什么？
2. 假设新增107后表中共七条记录：修改语句省略WHERE id = 107，哪些记录会被修改？删除语句省略同一条件，哪些记录会被删除？

## 当前记录

- 教师提供独立样本数据库和本说明；writes.sql由学习者亲手创建。
- 教师已用本机Python3.12的sqlite3 CLI在独立临时数据库预检新增、修改、跨进程重开查询和删除，四步通过，原六条样本保持原样；另已准备本节数据库，当前仅含101—106，尚无107。此记录不是学习者执行结果。
- 学习者已保存writes.sql，新增、按主键修改、按主键删除与查询语句均已按实际文件核对。标题使用DAY96和英文冒号，与示例文字不同但不影响功能；未代改学习者代码。
- 两道理解题均答对：能说明SET的等号指定新值，WHERE的等号比较筛选；知道省略WHERE时修改／删除涉及所有记录。该关键理解检查通过，不追加题目。
- 只读查询本节数据库，当前为原来的101—106六条记录，107不存在，符合最后一步的预期状态；当前状态本身不能证明全部中间步骤均已执行，尚未收到逐步运行结果。
- Day96 Git待学习者提交；不将教师预检记为学习者执行结果。
