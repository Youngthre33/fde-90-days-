import psycopg

from ticket_app.config import settings


def find_ticket_by_id(ticket_id):
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
    finally:
        connection.close()

    if row is None:
        return None

    return {
        "id": row[0],
        "title": row[1],
        "status": row[2],
    }


if __name__ == "__main__":
    ticket = find_ticket_by_id(3)
    print("查询结果：", ticket)
