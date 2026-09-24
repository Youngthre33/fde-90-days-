-- 1. 正常新增：只提供编号和标题，没有提供状态
INSERT INTO tickets (id, title)
VALUES (201, 'Day97：客户无法登录');

-- 查看新增结果
SELECT id, title, status
FROM tickets
ORDER BY id;

-- 2. 尝试新增一条没有标题的工单
INSERT INTO tickets (id, title)
VALUES (202, NULL);

-- 3. 尝试新增一条标题只有三个普通空格的工单
INSERT INTO tickets (id, title)
VALUES (203, '   ');

-- 4. 尝试再次使用已经存在的编号201
INSERT INTO tickets (id, title)
VALUES (201, 'Day97：客户无法登录');

-- 5. 尝试把201的状态改成不在规定范围内的closed
UPDATE tickets
SET status = 'closed'
WHERE id = 201;

-- 6. 尝试把201的状态改成NULL
UPDATE tickets
SET status = NULL
WHERE id = 201;

-- 最后统一查询，看看真正保存下来的数据
SELECT id, title, status
FROM tickets
ORDER BY id;