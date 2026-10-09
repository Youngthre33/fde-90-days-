import psycopg
import pytest

from ticket_app import ticket_repository


def test_create_and_find_ticket():
    assert ticket_repository.list_tickets(None, 100) == []

    created = ticket_repository.create_new_ticket("测试：登录失败")
    found = ticket_repository.find_ticket_by_id(created["id"])

    assert created["title"] == "测试：登录失败"
    assert created["status"] == "open"
    assert found == created



def test_update_ticket_status():
    assert ticket_repository.list_tickets(None, 100) == []

    created = ticket_repository.create_new_ticket("测试：打印机离线")
    updated = ticket_repository.update_ticket_by_id(
        created["id"],
        {"status": "done"},
    )

    assert updated == {
        "id": created["id"],
        "title": "测试：打印机离线",
        "status": "done",
    }
    assert ticket_repository.find_ticket_by_id(created["id"]) == updated




def test_delete_only_target_ticket():
    assert ticket_repository.list_tickets(None, 100) == []

    target = ticket_repository.create_new_ticket("测试：准备删除")
    kept = ticket_repository.create_new_ticket("测试：需要保留")

    deleted = ticket_repository.delete_ticket_by_id(target["id"])

    assert deleted == target
    assert ticket_repository.find_ticket_by_id(target["id"]) is None
    assert ticket_repository.find_ticket_by_id(kept["id"]) == kept
    assert ticket_repository.list_tickets(None, 100) == [kept]
    assert ticket_repository.delete_ticket_by_id(target["id"]) is None




def test_reject_empty_title():
    assert ticket_repository.list_tickets(None, 100) == []

    kept = ticket_repository.create_new_ticket("测试：正常工单")

    with pytest.raises(psycopg.IntegrityError):
        ticket_repository.create_new_ticket("")

    assert ticket_repository.list_tickets(None, 100) == [kept]


def test_update_rolls_back_title_when_status_is_invalid():
    created = ticket_repository.create_new_ticket("测试：保留原始标题")

    with pytest.raises(psycopg.IntegrityError):
        ticket_repository.update_ticket_by_id(
            created["id"],
            {"title": "测试：这次标题修改也应撤回", "status": "waiting"},
        )

    assert ticket_repository.find_ticket_by_id(created["id"]) == created
    assert ticket_repository.list_tickets(None, 100) == [created]
