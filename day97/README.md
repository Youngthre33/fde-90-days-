# Day97：让数据库拒绝不合规则的数据

## 今天的实际用途

Day94建立表，Day95查询，Day96写入／修改／删除；今天在表中声明数据规则，拒绝缺少标题、无效状态和重复编号。客户系统需要把可靠的数据长期保存：Day98由Python连接数据库，Day99替换后端内存存储。当前实际Day97对应原规划Day95的约束与数据质量。

本节仍由学习者在终端直接操作本机SQLite，输入SQL、在终端看结果，不需要启动5500或8001。规则写进数据库表后，在正常启用约束的连接中，网页后端、导入脚本或手工SQL都要遵守。现有网页后端尚未接入这个练习库。

## 1. 亲手建立带规则的新表

在本目录创建schema.sql，输入并保存：

```sql
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL CHECK (length(trim(title)) > 0),
    status TEXT NOT NULL DEFAULT 'open'
        CHECK (status IN ('open', 'in_progress', 'done'))
);
```

在仓库根目录的PowerShell执行：

```powershell
.\.venv\Scripts\python.exe -X utf8 -m sqlite3 .\day97\tickets.db (Get-Content -LiteralPath .\day97\schema.sql -Raw -Encoding utf8)
```

命令读取SQL文件并执行，生成独立的day97/tickets.db和空表。本目录初始没有数据库，不复制Day96数据库。IF NOT EXISTS只在表不存在时创建；编辑schema.sql再重跑，不会给已存在的旧表自动补规则。新建练习库是本课安排，真实客户旧库的结构变更后面学习迁移。

## 2. 打开交互入口，逐条运行检查

```powershell
.\.venv\Scripts\python.exe -X utf8 -m sqlite3 .\day97\tickets.db
```

出现sqlite>后，执行下面的SQL。另新建checks.sql，亲手保存这些语句；每次选中一整条（含分号）粘贴到sqlite>并按Enter。不要把整份文件交给只执行单条SQL的命令参数。本例按顺序首次执行，五条报错是预期结果，看到错误后继续下一条，不删库重建。

### ① 正常新增，省略状态

```sql
INSERT INTO tickets (id, title)
VALUES (201, 'Day97：客户无法登录');
```

预期成功。查询一次：

```sql
SELECT id, title, status
FROM tickets
ORDER BY id;
```

预期(201, 'Day97：客户无法登录', 'open')，状态由数据库的默认值提供。

### ② 标题给NULL

```sql
INSERT INTO tickets (id, title)
VALUES (202, NULL);
```

预期失败，错误中包含NOT NULL constraint failed: tickets.title。

### ③ 标题只有三个普通空格

```sql
INSERT INTO tickets (id, title)
VALUES (203, '   ');
```

预期失败，错误中包含CHECK constraint failed: length(trim(title)) > 0。

### ④ 再新增同一个编号

```sql
INSERT INTO tickets (id, title)
VALUES (201, 'Day97：客户无法登录');
```

预期失败，错误中包含UNIQUE constraint failed: tickets.id。失败原因是编号重复，不是标题重复；本表允许不同工单标题相同。

### ⑤ 修改成无效状态

```sql
UPDATE tickets
SET status = 'closed'
WHERE id = 201;
```

预期失败，错误中包含CHECK constraint failed: status IN ('open', 'in_progress', 'done')。

### ⑥ 把状态改成NULL

```sql
UPDATE tickets
SET status = NULL
WHERE id = 201;
```

预期失败，错误中包含NOT NULL constraint failed: tickets.status。DEFAULT不会把本次明确指定的NULL替换为open。

### ⑦ 统一查询最终结果

再执行上面的SELECT，仍应只有(201, 'Day97：客户无法登录', 'open')。失败的新增没有留下202／203，重复新增没有产生第二条201，失败的修改没有改变原状态。最后输入.quit退出到PowerShell。.quit不写进SQL文件。

## 3. 跑通后回看规则

| 写法 | 本例作用 |
| --- | --- |
| id INTEGER PRIMARY KEY | 工单编号作为唯一标识，拒绝重复编号 |
| title TEXT NOT NULL | 标题不能为NULL |
| CHECK (length(trim(title)) > 0) | 去掉首尾普通空格后至少有一个字符 |
| status TEXT NOT NULL | 状态不能为NULL |
| DEFAULT 'open' | 新增时省略status，由数据库补open |
| CHECK (status IN (...)) | 状态必须属于列出的三种 |

NOT NULL拒绝NULL，不等于拒绝空字符串。NULL是不提供具体值的标记，不加引号；''是长度0的字符串；'   '是含普通空格的字符串。不要写成文本'NULL'。

title的CHECK按从里往外理解：trim(title)得到去掉首尾普通空格的字符串，length(...)计算其字符数，> 0要求至少有一个字符。CHECK使用结果判断是否接受记录，不会自动把去空格后的字符串写回title；例如'  网络故障  '通过时仍保存原来的两侧空格。这里默认trim只针对普通空格，不宣称覆盖所有空白字符。

status IN ('open', 'in_progress', 'done')表示状态必须是这三个值之一。NOT NULL和CHECK搭配，分别拒绝NULL及不在范围内的字符串。DEFAULT用于新增时省略该列；明确给NULL或空字符串不会自动用默认值纠正。

UNIQUE表示唯一规则，例如将来要求客户编号不能重复时可用。本例id主键已经负责编号唯一，不另加重复规则；title允许重复，不设置UNIQUE。外键FOREIGN KEY用于表之间的关联，例如工单填写的负责人编号必须能在用户表里找到。等引入用户表再实作；SQLite中后续还需在连接上启用外键检查，今天没有第二张表和外键操作。

参考：[SQLite建表、默认值与约束](https://www.sqlite.org/lang_createtable.html)、[SQLite字符串函数](https://www.sqlite.org/lang_corefunc.html)、[SQLite外键](https://www.sqlite.org/foreignkeys.html)。

## 4. 前端、后端、数据库各负责什么

| 位置 | 实际工作 |
| --- | --- |
| 前端（浏览器里的JavaScript） | 用户填写时及时提示，提高操作体验 |
| 后端（服务器上运行的Python） | 校验请求、权限和业务规则，给调用者适合的响应 |
| 数据库（本课SQLite表） | 在保存时拒绝违反表规则的数据 |

后台导入脚本、手工SQL等入口可以绕过网页，也不一定调用同一个Python接口，所以数据库仍需要约束。规则应协调一致，不能用数据库约束替代权限或所有业务逻辑。

```text
今天：你写SQL → SQLite检查表规则 → 合规就保存，不合规就拒绝 → 终端显示结果
以后：客户操作网页 → 浏览器发请求 → Python后端检查并写库 → 数据库检查 → 后端把结果回给浏览器
```

今天的报错来自数据库，显示给正在操作终端的你，不是HTTP状态码。未来Python要接住数据库错误并给浏览器合适的响应，不应把原始数据库报错直接展示给客户。

## 5. 完整操作后两道理解题

1. 网页和Python后端都检查状态，数据库为什么还要写CHECK？
2. 创建工单时，status分别省略、明确写NULL、写成''，按本表规则会分别怎样？哪一种使用默认值？只预测，不增加运行步骤。

## 当前记录

- 教师已创建本说明及数据库忽略规则；schema.sql、checks.sql和本节数据库留给学习者亲手创建，尚未替学习者写核心SQL或建表。
- 已在独立临时数据库通过本机Python3.12 sqlite3 CLI预检：默认值成功、五条违规操作对应报错、交互工具报错后可继续，最终只有201且状态仍为open；没有修改任何前课数据库。该记录不代表学习者已执行。
- 学习者已保存schema.sql和checks.sql，内容按实际文件核对正确；只读检查day97/tickets.db，表定义已包含本节全部规则，当前仅有(201, 'Day97：客户无法登录', 'open')。这确认实际建表及当前保存结果，不冒称已观察五次错误的逐条输出；本轮未重跑写操作。
- 理解题已作答：第二题正确判断省略status用默认值，NULL和空格字符串会报错；讲评补充空字符串''与空格字符串' '不同，但本表两者都违反状态CHECK，NULL则违反NOT NULL。
- 第一题知道模块职责不同，但把原因归为不同网页端口和服务器规则。本轮校准：数据库是保存数据的组件，8001是Python后端在当前练习中的入口；来自不同网页／端口但仍经过同一接口的请求仍会执行接口校验。数据库规则的关键是手工SQL、导入脚本等可以不经过网页和接口而直接写数据库，同时也防止后端遗漏。
- 不追加理解题。Git待学习者提交，收尾同时纳入day96/README.md的完成记录更新。
