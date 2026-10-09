import pytest
from fastapi.testclient import TestClient
from ticket_app.config import settings 
from ticket_app.main import app


client = TestClient(app, headers={"Authorization": "Bearer test-admin-token"},)


# schema的建立和清理由conftest统一管理；这里只准备API场景的数据。
@pytest.fixture(autouse=True)
def configure_test_tokens(monkeypatch):
    monkeypatch.setattr(settings, "staff_token", "test-staff-token")
 

@pytest.fixture(autouse=True)   
def seeded_tickets(isolated_database):
    with isolated_database() as connection:
        with connection.cursor() as cursor:
            cursor.executemany(
                "INSERT INTO tickets (id, title, status) "
                "OVERRIDING SYSTEM VALUE VALUES (%s, %s, %s)",
                [
                    (101, "API 登录失败", "open"),
                    (102, "API 修改发票", "in_progress"),
                    (103, "支付失败", "open"),
                    (104, "导出报表失败", "done"),
                ],
            )
        # 手工填写101—104不会推进identity序列，下一次自动编号应为105。
        connection.execute(
            "SELECT setval(pg_get_serial_sequence('tickets', 'id'), 104, true)"
        )


@pytest.fixture
def events_database(isolated_database, seeded_tickets):
    with isolated_database() as connection:
        with connection.cursor() as cursor:
            cursor.executemany(
                "INSERT INTO ticket_events (id, ticket_id, note) "
                "OVERRIDING SYSTEM VALUE VALUES (%s, %s, %s)",
                [
                    (3, 101, "已完成处理"),
                    (1, 102, "另一张工单的记录"),
                    (2, 101, "已联系客户"),
                ],
            )
        connection.execute(
            "SELECT setval(pg_get_serial_sequence('ticket_events', 'id'), 3, true)"
        )

    return isolated_database


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


# 分页按筛选后的结果计算，顺序由 API 的 order 参数控制。
def test_list_tickets_pagination():
    for params, expected_ids in [
        ({"limit": 2, "page": 2, "order": "asc"}, [103, 104]),
        ({"limit": 2, "page": 2, "order": "desc"}, [102, 101]),
        ({"status": "open", "limit": 1, "page": 2}, [103]),
        ({"status": "open", "limit": 1, "page": 2, "order": "desc"}, [101]),
        ({"status": "open", "limit": 1, "page": 3}, []),
    ]:
        response = client.get("/tickets", params=params)
        assert response.status_code == 200
        assert [ticket["id"] for ticket in response.json()] == expected_ids


def test_reject_invalid_list_parameters():
    for params in [
        {"limit": 0},
        {"limit": 101},
        {"page": 0},
        {"order": "invalid"},
    ]:
        response = client.get("/tickets", params=params)
        assert response.status_code == 422, params


# 同一张工单可以有多条记录；没有记录与工单不存在是不同结果。
def test_ticket_events_api(events_database):
    response = client.get("/tickets/101/events")
    assert response.status_code == 200
    assert response.json() == [
        {"id": 2, "ticket_id": 101, "note": "已联系客户"},
        {"id": 3, "ticket_id": 101, "note": "已完成处理"},
    ]

    empty_response = client.get("/tickets/103/events")
    assert empty_response.status_code == 200
    assert empty_response.json() == []

    missing_response = client.get("/tickets/999/events")
    assert missing_response.status_code == 404
    assert missing_response.json() == {"detail": "工单不存在"}
    assert client.get("/tickets/0/events").status_code == 422


# 删除工单时清理它自己的记录，另一张工单及其记录应保留。
def test_delete_ticket_cascades_only_its_events(events_database):
    response = client.delete("/tickets/101")
    assert response.status_code == 204
    assert client.get("/tickets/101/events").status_code == 404
    assert client.get("/tickets/102").status_code == 200

    kept_response = client.get("/tickets/102/events")
    assert kept_response.status_code == 200
    assert kept_response.json() == [
        {"id": 1, "ticket_id": 102, "note": "另一张工单的记录"},
    ]

    with events_database() as connection:
        assert connection.execute(
            "SELECT id, ticket_id FROM ticket_events ORDER BY id"
        ).fetchall() == [(1, 102)]
        assert connection.execute(
            "SELECT ticket_events.id FROM ticket_events "
            "LEFT JOIN tickets ON tickets.id = ticket_events.ticket_id "
            "WHERE tickets.id IS NULL"
        ).fetchall() == []
