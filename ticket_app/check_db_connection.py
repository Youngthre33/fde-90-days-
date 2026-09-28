import psycopg

from ticket_app.config import settings


connection = psycopg.connect(
    host=settings.db_host,
    port=settings.db_port,
    dbname=settings.db_name,
    user=settings.db_user,
    password=settings.db_password,
    connect_timeout=5,
)

try:
    print("连接成功，数据库：", connection.info.dbname)
finally:
    connection.close()

print("连接是否已关闭：", connection.closed)
