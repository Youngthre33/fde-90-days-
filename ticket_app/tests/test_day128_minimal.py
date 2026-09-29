from ticket_app import ticket_repository


def test_create_and_find_ticket():
    created = ticket_repository.create_new_ticket(
        "Day128：pytest新增并查询"
    )

    found = ticket_repository.find_ticket_by_id(
        created["id"]
    )

    assert found == created