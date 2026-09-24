-- Teacher-provided sample data for SELECT practice. Run once on an empty table.
INSERT INTO tickets (id, title, status)
VALUES
    (101, 'API 登录失败', 'open'),
    (102, 'API 修改发票', 'in_progress'),
    (103, '支付失败', 'open'),
    (104, '导出报表失败', 'done'),
    (105, '发票抬头错误', 'open'),
    (106, '客户资料重复', 'done');
