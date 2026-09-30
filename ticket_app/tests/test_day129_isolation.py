from ticket_app import ticket_repository


def test_first_ticket_starts_empty():
    assert ticket_repository.list_tickets(status=None, limit=10) == []

    created = ticket_repository.create_new_ticket("Day129：第一项测试")

    assert ticket_repository.find_ticket_by_id(created["id"]) == created


def test_second_ticket_starts_empty():
    assert ticket_repository.list_tickets(status=None, limit=10) == []

    created = ticket_repository.create_new_ticket("Day129：第二项测试")

    assert ticket_repository.find_ticket_by_id(created["id"]) == created