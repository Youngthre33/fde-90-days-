from ticket_app import ticket_repository


def test_update_status_is_saved():
    assert ticket_repository.list_tickets(status=None, limit=100) == []

    created = ticket_repository.create_new_ticket("Day130: 打印机离线")

    updated = ticket_repository.update_ticket_by_id(
        created["id"],
        {"status": "done"},
    )

    assert updated == {
        "id": created["id"],
        "title": "Day130: 打印机离线",
        "status": "done",
    }

    assert ticket_repository.find_ticket_by_id(created["id"]) == updated
