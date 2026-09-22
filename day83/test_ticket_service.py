from day82.ticket_service import (
    find_ticket_by_id,
    list_tickets,
)

# ==================================================
# 1. 查找存在的工单
# ==================================================

def test_find_existing_ticket():
    ticket = find_ticket_by_id(101)



    assert ticket is not None
    assert ticket ["id"] == 101
    assert ticket ["title"] == "API 登录失败"
    assert ticket ["status"] == "open"


# ==================================================
# 2. 查找不存在的工单
# ==================================================

def test_find_missing_ticket():
    ticket = find_ticket_by_id(999)    

    assert ticket is None


# ==================================================
# 3. 按状态筛选工单
# ==================================================

def test_list_open_tickets():
    result = list_tickets(
        status ="open",
        limit=10,
    )

    assert len(result) == 2
    assert result[0]["id"] == 101
    assert result[1]["id"] == 103


# ==================================================
# 4. 限制返回的工单数量
# ==================================================

def test_list_tickets_with_limit():
    result = list_tickets(
        status=None,
        limit=2,
    )

    assert len(result) == 2
    assert result[0]["id"] == 101
    assert result[1]["id"] == 102


