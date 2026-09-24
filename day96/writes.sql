INSERT INTO tickets (id, title, status)
VALUES (107, 'DAY96:客户无法登录', 'open');


SELECT id, title, status
FROM tickets
WHERE id = 107;


UPDATE tickets
SET title = 'DAY96: 登录问题已确认',
    status = 'in_progress'
WHERE id = 107;


DELETE FROM tickets
WHERE id = 107;

SELECT id, title, status
FROM tickets
ORDER BY id;