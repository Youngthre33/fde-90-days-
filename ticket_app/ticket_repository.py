import psycopg

from ticket_app.config import settings


def get_connection():
    return psycopg.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        connect_timeout=5,
    )


def row_to_ticket(row):
    if row is None:
        return None

    return {
        "id": row[0],
        "title": row[1],
        "status": row[2],
    }




def find_ticket_by_id(ticket_id: int):
    with get_connection() as connection:
        cursor = connection.execute(
            "SELECT id, title, status FROM tickets WHERE id = %s",
            (ticket_id,),
        )
        row = cursor.fetchone()

    return row_to_ticket(row)




def list_tickets(
    status: str | None,
    limit: int,
    offset: int = 0,
    order: str = "asc",
):
    if order == "desc":
        direction = "DESC"
    else:
        direction = "ASC"

    with get_connection() as connection:
        if status is None:
            cursor = connection.execute(
                "SELECT id, title, status FROM tickets "
                f"ORDER BY id {direction} LIMIT %s OFFSET %s",
                (limit, offset),
            )
        else:
            cursor = connection.execute(
                "SELECT id, title, status FROM tickets "
                f"WHERE status = %s ORDER BY id {direction} "
                "LIMIT %s OFFSET %s",
                (status, limit, offset),
            )
        rows = cursor.fetchall()

    tickets = []
    for row in rows:
        tickets.append(row_to_ticket(row))
    return tickets


def list_ticket_events(ticket_id: int):
    with get_connection() as connection:
        cursor = connection.execute(
            "SELECT ticket_events.id, ticket_events.ticket_id, "
            "ticket_events.note "
            "FROM tickets "
            "LEFT JOIN ticket_events ON ticket_events.ticket_id = tickets.id "
            "WHERE tickets.id = %s ORDER BY ticket_events.id",
            (ticket_id,),
        )
        rows = cursor.fetchall()

    if not rows:
        return None

    events = []
    for row in rows:
        if row[0] is not None:
            events.append({
                "id": row[0],
                "ticket_id": row[1],
                "note": row[2],
            })
    return events


def create_new_ticket(title: str):
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO tickets (title) VALUES (%s) "
            "RETURNING id, title, status",
            (title,),
        )
        row = cursor.fetchone()

    return row_to_ticket(row)


def update_ticket_by_id(ticket_id: int, update_data: dict):
    with get_connection() as connection:
        if "title" in update_data:
            connection.execute(
                "UPDATE tickets SET title = %s WHERE id = %s",
                (update_data["title"], ticket_id),
            )

        if "status" in update_data:
            connection.execute(
                "UPDATE tickets SET status = %s WHERE id = %s",
                (update_data["status"], ticket_id),
            )

        cursor = connection.execute(
            "SELECT id, title, status FROM tickets WHERE id = %s",
            (ticket_id,),
        )
        row = cursor.fetchone()

    return row_to_ticket(row)


def delete_ticket_by_id(ticket_id: int):
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM tickets WHERE id = %s "
            "RETURNING id, title, status",
            (ticket_id,),
        )
        row = cursor.fetchone()

    return row_to_ticket(row)
