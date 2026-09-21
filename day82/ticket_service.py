from day82.ticket_store import tickets


def find_ticket_by_id(ticket_id: int):
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket

    return None


def list_tickets(
    status: str | None,
    limit: int,
):
    filtered_tickets = []

    for ticket in tickets:
        if status is None or ticket["status"] == status:
            filtered_tickets.append(ticket)

    return filtered_tickets[:limit]


def create_new_ticket(title: str):
    created_ticket = {
        "id": tickets[-1]["id"] + 1,
        "title": title,
        "status": "open",
    }

    tickets.append(created_ticket)

    return created_ticket


def update_ticket_by_id(
    ticket_id: int,
    update_data: dict,
):
    ticket = find_ticket_by_id(ticket_id)

    if ticket is None:
        return None

    ticket.update(update_data)

    return ticket


def delete_ticket_by_id(ticket_id: int):
    ticket = find_ticket_by_id(ticket_id)

    if ticket is None:
        return None

    tickets.remove(ticket)

    return ticket
