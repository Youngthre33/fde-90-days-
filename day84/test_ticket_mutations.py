from copy import deepcopy

import pytest

from day82.ticket_service import (
    create_new_ticket,
    delete_ticket_by_id,
    find_ticket_by_id,
    update_ticket_by_id,
)
from day82.ticket_store import tickets


# ==================================================
# 1. 每个测试开始前准备数据，结束后恢复数据
# ==================================================

@pytest.fixture(autouse=True)
def reset_tickets():
    original_tickets = deepcopy(tickets)

    tickets[:] = [
        {"id": 101, "title": "API 登录失败", "status": "open"},
        {"id": 102, "title": "API 修改发票", "status": "in_progress"},
        {"id": 103, "title": "支付失败", "status": "open"},
        {"id": 104, "title": "导出报表失败", "status": "done"},
    ]

    yield

    tickets[:] = original_tickets


# ==================================================
# 2. 创建工单
# ==================================================

def test_create_ticket():
    created_ticket = create_new_ticket("客户无法提供发票")

    assert created_ticket == {
        "id": 105,
        "title": "客户无法提供发票",
        "status": "open",
    }
    assert len(tickets) == 5
    assert find_ticket_by_id(105) is created_ticket


# ==================================================
# 3. 修改工单
# ==================================================

def test_update_ticket():
    original_ticket = find_ticket_by_id(101)

    updated_ticket = update_ticket_by_id(
        101,
        {"status": "done"},
    )

    assert updated_ticket is original_ticket
    assert updated_ticket == {
        "id": 101,
        "title": "API 登录失败",
        "status": "done",
    }


# ==================================================
# 4. 删除工单
# ==================================================

def test_delete_ticket():
    original_ticket = find_ticket_by_id(103)

    deleted_ticket = delete_ticket_by_id(103)

    assert deleted_ticket is original_ticket
    assert len(tickets) == 3
    assert find_ticket_by_id(103) is None


# ==================================================
# 5. 修改不存在的工单
# ==================================================

def test_update_missing_ticket():
    before = deepcopy(tickets)

    result = update_ticket_by_id(
        999,
        {"status": "done"},
    )

    assert result is None
    assert tickets == before

    
# ==================================================
# 6. 删除不存在的工单
# ==================================================

def test_delete_missing_ticket():
    before = deepcopy(tickets)

    result = delete_ticket_by_id(999)

    assert result is None
    assert tickets == before
