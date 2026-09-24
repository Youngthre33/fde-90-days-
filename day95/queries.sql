SELECT id, title, status
FROM tickets
ORDER BY id;


SELECT id, title, status
FROM tickets
WHERE status = 'open'
ORDER BY id;

SELECT id, title, status
FROM tickets
ORDER BY id DESC;

SELECT id, title, status
FROM tickets
WHERE status = 'open'
ORDER BY id DESC

LIMIT 2;