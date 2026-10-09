from ticket_app import ticket_repository


def find_ticket_by_id(ticket_id: int):
    return ticket_repository.find_ticket_by_id(ticket_id)


def list_tickets(
    status: str | None,
    limit: int,
    page: int = 1,
    order: str = "asc",
):
    offset = (page - 1) * limit

    return ticket_repository.list_tickets(
        status=status,
        limit=limit,
        offset=offset,
        order=order,
    )



def list_ticket_events(ticket_id: int):
    return ticket_repository.list_ticket_events(ticket_id)


def create_new_ticket(title: str):
    return ticket_repository.create_new_ticket(title)


def update_ticket_by_id(ticket_id: int, update_data: dict):
    return ticket_repository.update_ticket_by_id(ticket_id, update_data)


def delete_ticket_by_id(ticket_id: int):
    return ticket_repository.delete_ticket_by_id(ticket_id)
