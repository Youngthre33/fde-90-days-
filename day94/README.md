# Day 94：把工单设计成数据库表

## 本节的实际目标

Day93已观察到后端重启使临时工单消失。现在开始学习数据库，为后续长期保存数据准备。
今天把已有工单的id、title、status设计成表的列，用SQL创建一张空表，并从新的命令进程重新打开同一个数据库文件确认表定义仍在。
本节数据库尚未接入Day90后端；网页仍使用原来的内存数据，不会自动读写新文件。

## 从已有工单认识表、行、列和主键

一条Python工单字典：

```python
{"id": 101, "title": "API 登录失败", "status": "open"}
```

可以设计成tickets表中的一行。下面是映射示意，尚未写入本节数据库：

| id | title | status |
| --- | --- | --- |
| 101 | API 登录失败 | open |
| 102 | API 修改发票 | in_progress |
| 103 | 支付失败 | open |

- 表：把同一类记录组织起来，这里叫tickets。
- 列：每条记录中一个有名称的字段，这里是id、title、status。
- 行：一条具体记录，例如编号101的工单。
- 主键：用来唯一识别某一条记录的字段；这里选择id。它不表示第几行，也不保证查询时的显示顺序。

主键唯一性在同一张表中成立。不同工单标题可以相同，不能只靠标题定位工单。
本节不承诺编号连续或删除后永不复用，后续学习写入时再说明编号生成。

## SQLite和两个文件的分工

SQLite是处理数据库读写的软件，可以将结构和数据保存在一个本地文件里，不需要额外启动数据库服务器或新开数据库端口。
现有Python3.12带有sqlite3命令行工具，本节使用它执行SQL。SQL是给数据库下达操作指令的语言。[Python sqlite3官方说明](https://docs.python.org/3.12/library/sqlite3.html#command-line-interface)

| 文件 | 谁创建 | 里面是什么 |
| --- | --- | --- |
| `schema.sql` | 学习者在编辑器里编写 | 创建表的SQL指令，是可读文本 |
| `tickets.db` | 执行指令时由SQLite创建 | 表结构以及未来写入的记录，使用数据库工具读取 |

schema可以理解为数据结构设计；创建.sql文件本身不会执行指令，也不会自动保存网页工单。
本地生成的Day94数据库文件已加入.gitignore；以后提交本节的SQL与说明，数据库按指令重新生成。

## 亲手写建表指令

在day94中新建schema.sql，写入并保存：

```sql
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY,
    title TEXT,
    status TEXT
);
```

逐段含义：

| 代码 | 含义 |
| --- | --- |
| `CREATE TABLE` | 创建一张表 |
| `IF NOT EXISTS` | 同名表不存在时才创建，已存在则跳过 |
| `tickets` | 这张表的名称 |
| 括号中的三行 | 定义三列，列之间用逗号分隔 |
| `id INTEGER PRIMARY KEY` | 将id设为整数主键，用来识别记录 |
| `title TEXT` | title列声明为文本，用来存标题 |
| `status TEXT` | status列声明为文本，用来存状态 |
| `;` | 结束这条SQL指令 |

SQLite普通表的类型规则较宽松，不要把TEXT理解为与Pydantic完全相同的严格类型校验。本节还没有限制标题非空或状态只能取三个值，Day97再学习约束。
修改schema.sql后再次运行IF NOT EXISTS不会修改已经存在的表结构。[SQLite CREATE TABLE说明](https://www.sqlite.org/lang_createtable.html)

## 一次执行与检查

在仓库根目录的空闲PowerShell终端执行。无需启动或停止5500和8001，这个练习独立操作数据库文件。

```powershell
.\.venv\Scripts\python.exe -m sqlite3 .\day94\tickets.db (Get-Content -LiteralPath .\day94\schema.sql -Raw)
```

`-m sqlite3`运行Python提供的数据库工具；后面指定数据库文件路径，括号内的Get-Content读取整个SQL文件并作为指令传给工具。
数据库文件不存在时会创建；建表成功通常没有额外文字输出，命令结束后回到PowerShell提示符。

接着查看列定义：

```powershell
.\.venv\Scripts\python.exe -m sqlite3 .\day94\tickets.db "SELECT name, type, pk FROM pragma_table_info('tickets');"
```

这是一条用于检查表结构的查询，选出列名、声明类型、主键标记。本节将它作为检查工具使用；SELECT查询在Day95继续学习。
预期输出：

```text
('id', 'INTEGER', 1)
('title', 'TEXT', 0)
('status', 'TEXT', 0)
```

本表中最后的1表示id是主键，0表示另外两列不是主键。这里输出的是三列的定义，不是三张工单。[SQLite表结构检查说明](https://www.sqlite.org/pragma.html#pragma_table_info)
建表命令结束后，那个程序已经退出；检查命令又启动一个新程序，打开同一个tickets.db并读出三列。因此这两条命令就能说明表定义已保存在文件里，不依赖前一次程序继续运行。
目前还没有执行写入记录的指令，因此表中没有工单；不能据此声称网页工单已经持久化。

## 对象、JSON和数据库记录的对应

| 形式 | 当前用途 |
| --- | --- |
| Python字典／JavaScript对象 | 程序运行时处理一条工单的数据 |
| JSON | 本项目中用于浏览器与后端之间传递数据的文本格式 |
| 数据库表中的行 | 以列的形式组织记录，写入并提交到文件数据库后可在程序重启后读取 |

它们可以表达同一条工单的信息，但不会自动互相转换。仅仅建表，不会把后端的tickets列表搬过来。

## 本节记录与下一步

- 教师已用当前Python3.12.5／SQLite3.45.3，在独立临时文件中预检建表、重复建表、新进程读取列定义和空表记录数；临时文件已清理，没有修改后端数据。
- 学习者已亲手编写schema.sql、执行建表并提供表结构输出。助手核对数据库现有记录数为0，并将学习者误写的stutus在SQL文件与已有表中统一更正为status；未插入工单，尚未连接网页后端。
- 结构查询中pk不是工单id的值。它表示列在主键中的位置，非主键为0；此表只有id作为主键，所以id的pk为1。
- 三道理解小测已回答：学习者能区分工单编号105与主键标记1，理解仅修改SQL文件不会自动改变数据库。对建表尚未完成应用持久化的判断正确，但把当前数据位置说成只有网页端；本次校准为“浏览器已经请求Python后端，后端目前保存到内存列表，后续让Python改为读写数据库，浏览器继续通过后端访问”。此项在Python接数据库时再对照，不额外增加测验。
- 本节建表与检查完成，Git提交待学习者操作；提交.gitignore、schema.sql和README，本地生成的tickets.db已忽略。
- Day95：SELECT、筛选、排序、限制数量；Day96：INSERT、UPDATE、DELETE；Day97：数据约束；Day98：Python连接与操作数据库；Day99：把后端内存存储换成数据库。
- 这些内容合起来，才形成“网页操作 → 后端处理 → 数据库保存 → 下次启动仍能读取”的完整功能。
