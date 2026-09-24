# Day 95：查询、筛选、排序和限制数量

## 今天的实际用途

客服想只查看待处理工单，或每次只显示几条记录，就需要查询、筛选、排序和限制数量。
以前这些工作由Python遍历列表完成；今天用SQL让数据库完成。当前由学习者在终端直接发SQL，后续由Python后端执行，浏览器仍通过后端访问。
本节不连接网页，不改变当前后端的内存存储方式。下一节Day96学习写入、修改和删除，后续再接Python与整个应用。

## 练习数据

复用Day94的表设计，使用独立文件day95/tickets.db，里面有六条专用样本：

| id | title | status |
| --- | --- | --- |
| 101 | API 登录失败 | open |
| 102 | API 修改发票 | in_progress |
| 103 | 支付失败 | open |
| 104 | 导出报表失败 | done |
| 105 | 发票抬头错误 | open |
| 106 | 客户资料重复 | done |

seed.sql是教师提供的样本写入指令，用来准备本节查询对象，写入语法在Day96讲解。它不代表学习者已经掌握INSERT。
本地数据库已忽略，提交SQL和说明即可。换电脑或文件尚未生成时，从仓库根目录首次运行下面两条命令：

```powershell
.\.venv\Scripts\python.exe -m sqlite3 .\day95\tickets.db (Get-Content -LiteralPath .\day94\schema.sql -Raw -Encoding utf8)
.\.venv\Scripts\python.exe -m sqlite3 .\day95\tickets.db (Get-Content -LiteralPath .\day95\seed.sql -Raw -Encoding utf8)
```

课堂中已准备好时直接进入下一步，不重复初始化。seed.sql用于空表；再次写入相同编号会报主键重复，不要为重跑查询而删除数据库或重建数据。

## 打开SQLite交互入口

在仓库根目录的空闲PowerShell终端执行：

```powershell
.\.venv\Scripts\python.exe -X utf8 -m sqlite3 .\day95\tickets.db
```

`-X utf8`让这次Python使用UTF-8模式，避免终端捕获中文输出时出现编码问题。
出现 `sqlite>` 后，在这个位置输入SQL。此时输入的内容交给SQLite工具处理，不是在给PowerShell下命令，也不是写Python代码。
每条SQL以分号结束，按Enter执行；换行未完成时出现 `...` 是等待剩余内容。退出输入 `.quit` 并按Enter，回到PowerShell。
已核对本机Python3.12工具支持以上交互方式。[Python sqlite3命令行说明](https://docs.python.org/3.12/library/sqlite3.html#command-line-interface)

## 亲手保存并运行四组查询

在day95中新建queries.sql，写入下面四条查询并保存。文件用于保存练习代码，保存不会自动执行。
每次选中一整条查询（包括最后的分号），复制到sqlite>后按Enter。不要把多条语句当作一条SQL参数传给上一节的单条命令入口。

### 1. 取出全部工单

```sql
SELECT id, title, status
FROM tickets
ORDER BY id;
```

SELECT指定要看哪些列，FROM指定从哪张表取，ORDER BY id按编号从小到大排列。预期编号为101、102、103、104、105、106。

### 2. 只查某个状态

```sql
SELECT id, title, status
FROM tickets
WHERE status = 'open'
ORDER BY id;
```

WHERE表示筛选条件；这里的等号比较状态是否等于open，不会把状态改成open。单引号中的open是文本值，status是列名。
先运行open版本，再只把文本值换成in_progress、done各运行一次；可以把两个变体也保存在queries.sql中。
预期：open为101、103、105；in_progress为102；done为104、106。

### 3. 编号从大到小

```sql
SELECT id, title, status
FROM tickets
ORDER BY id DESC;
```

DESC表示降序，这里是106、105、104、103、102、101；不写ASC或DESC时默认升序。
本例按编号排序，不把“编号最大”当作已知“创建时间最新”，因为表里还没有创建时间字段。

### 4. 查出编号最大的两条待处理工单

```sql
SELECT id, title, status
FROM tickets
WHERE status = 'open'
ORDER BY id DESC
LIMIT 2;
```

按业务含义理解为：筛出open → 让符合条件的记录按编号降序排列 → 最多返回前两条。
预期返回105和103，包括它们的title与status；LIMIT限制返回行数，不删除其余记录。

## 一次核对

| 查询 | 预期编号顺序 |
| --- | --- |
| 全部，按id升序 | 101、102、103、104、105、106 |
| open，按id升序 | 101、103、105 |
| in_progress，按id升序 | 102 |
| done，按id升序 | 104、106 |
| 全部，按id降序 | 106、105、104、103、102、101 |
| open，按id降序，最多两条 | 105、103 |

这些SELECT语句只读数据，不改变表内记录；ORDER BY也不把表永久改成某种显示顺序。
需要确定返回顺序时应明确写ORDER BY，不能依赖某次刚好观察到的顺序。[SQLite SELECT说明](https://www.sqlite.org/lang_select.html)

## 整块流程回顾

```text
学习者写一条SQL
  → 在sqlite>中提交指令
  → SQLite读取day95/tickets.db中的tickets表
  → 按查询条件得到本次结果
  → 命令行工具把每条结果显示为一行
```

SELECT id,title,status决定每行返回哪些字段；WHERE决定候选记录；ORDER BY决定顺序；LIMIT决定最多返回几行。
退出工具后数据库中的六条工单仍在。当前这些样本与网页后端内存中的工单是不同的数据，不会自动同步。

## 两道关键理解题

完成四组查询后，用自己的话回答，不需要为了答题再增加一整组测试。

1. 要把第四条改为查询“编号最大的两条已完成工单”，应改哪里？先预测返回的两个编号。
2. 如果第四条保留WHERE和LIMIT 2，却删除ORDER BY id DESC，还能保证返回编号最大的两条待处理工单吗？为什么？

## 记录

- 教师已在独立Day95文件中准备六条样本，只读核对全部／三状态／降序／筛选后限两条的编号结果，确认查询后仍有六条记录，并验证多行交互查询与.quit退出。初次工具捕获中文输出有编码问题，使用-X utf8后已核对中文正确。
- 学习者亲手写queries.sql并在交互入口运行；教师没有代写该查询文件，也没有操作网页后端工单或Day94数据库。
- 学习者已亲手保存queries.sql，四条主体查询已按实际文件核对，语法与练习一致；尚未收到逐项运行输出，不将教师预检冒充学习者运行结果。
- 两道小测已作答：第一题知道应改WHERE，但将done的降序结果写为104、106，正确顺序应为106、104；第二题知道去掉ORDER BY不能保证最大两条，但误认为未排序就一定按编号升序。当前校准为“写ORDER BY id或ASC才明确升序，写DESC为降序，省略ORDER BY不保证顺序”。不额外追加题目，后续练习继续对照。
- 已核对Git记录：f5997f8（Day 95: query and filter tickets with SQL），main与本地origin/main均指向该提交；之后queries.sql仅移除了LIMIT前的空行，语义不变。
- 本节提交包含.gitignore、seed.sql、queries.sql和README；不提交本地生成的数据库文件。
