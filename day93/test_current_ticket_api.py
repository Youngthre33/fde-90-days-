from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from day90.main import app
from day82.ticket_store import tickets


client = TestClient(app)


# ==================================================
# 每个测试开始前准备数据，结束后恢复数据
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
# 1. 健康检查接口
# ==================================================

def test_health_api():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ==================================================
# 2. 查询存在的工单
# ==================================================

def test_get_existing_ticket_api():
    response = client.get("/tickets/101")

    assert response.status_code == 200
    assert response.json() == {
        "id": 101,
        "title": "API 登录失败",
        "status": "open",
    }


# ==================================================
# 3. 查询不存在的工单
# ==================================================

def test_get_missing_ticket_api():
    response = client.get("/tickets/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "工单不存在"}


# ==================================================
# 4. 工单 ID 小于规定的最小值
# ==================================================

def test_get_zero_id_api():
    response = client.get("/tickets/0")

    assert response.status_code == 422


# ==================================================
# 5. 工单 ID 无法转换成整数
# ==================================================

def test_get_text_id_api():
    response = client.get("/tickets/abc")

    assert response.status_code == 422


# ==================================================
# 6. 创建工单，并通过 GET 查回
# ==================================================

def test_create_ticket_api():
    response = client.post(
        "/tickets",
        json={"title": "客户无法提供发票"},
    )

    assert response.status_code == 201

    created_ticket = response.json()
    assert created_ticket == {
        "id": 105,
        "title": "客户无法提供发票",
        "status": "open",
    }

    get_response = client.get("/tickets/105")
    assert get_response.status_code == 200
    assert get_response.json() == created_ticket


# ==================================================
# 7. 空标题被拒绝，列表保持不变
# ==================================================

def test_create_empty_title_api():
    before_response = client.get("/tickets")
    assert before_response.status_code == 200
    before = before_response.json()

    response = client.post(
        "/tickets",
        json={"title": ""},
    )

    assert response.status_code == 422

    after_response = client.get("/tickets")
    assert after_response.status_code == 200
    assert after_response.json() == before


# ==================================================
# 8. 修改标题，并通过 GET 查回
# ==================================================

def test_update_ticket_api():
    response = client.patch(
        "/tickets/101",
        json={"title": "登录问题已确认"},
    )

    assert response.status_code == 200

    updated_ticket = response.json()
    assert updated_ticket == {
        "id": 101,
        "title": "登录问题已确认",
        "status": "open",
    }

    get_response = client.get("/tickets/101")
    assert get_response.status_code == 200
    assert get_response.json() == updated_ticket


# ==================================================
# 9. 非法状态被拒绝，原工单保持不变
# ==================================================

def test_update_invalid_status_api():
    before_response = client.get("/tickets/101")
    assert before_response.status_code == 200
    before = before_response.json()

    response = client.patch(
        "/tickets/101",
        json={"status": "waiting"},
    )

    assert response.status_code == 422

    after_response = client.get("/tickets/101")
    assert after_response.status_code == 200
    assert after_response.json() == before


# ==================================================
# 10. 删除工单，确认查不到且不能重复删除
# ==================================================

def test_delete_ticket_api():
    response = client.delete("/tickets/103")

    assert response.status_code == 204
    assert response.text == ""

    get_response = client.get("/tickets/103")
    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "工单不存在"}

    second_delete_response = client.delete("/tickets/103")
    assert second_delete_response.status_code == 404
