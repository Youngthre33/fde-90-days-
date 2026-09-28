import psycopg

from ticket_app.config import settings


ticket_id = 3

connection = psycopg.connect(
    host=settings.db_host,
    port=settings.db_port,
    dbname=settings.db_name,
    user=settings.db_user,
    password=settings.db_password,
    connect_timeout=5,
)

try:
    cursor = connection.execute(
        "SELECT id, title, status FROM tickets WHERE id = %s",
        (ticket_id,),
    )
    row = cursor.fetchone()
    print("查询结果：", row)
finally:
    connection.close()
