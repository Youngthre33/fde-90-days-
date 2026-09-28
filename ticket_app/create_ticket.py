import psycopg

from ticket_app.config import settings


def create_ticket(title):
    with psycopg.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        connect_timeout=5,
    ) as connection:
        cursor = connection.execute(
            "INSERT INTO tickets (title) VALUES (%s) RETURNING id, title, status",
            (title,),
        )
        row = cursor.fetchone()

    print("连接是否已关闭：", connection.closed)

    return {
        "id": row[0],
        "title": row[1],
        "status": row[2],
    }


if __name__ == "__main__":
    ticket = create_ticket("Day119：with成功提交")
    print("新增结果：", ticket)
