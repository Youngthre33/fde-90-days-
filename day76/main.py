from typing import Literal

from fastapi import FastAPI, Path, Query


app = FastAPI(
    title="工单系统 API",
    description="Day 76：使用查询参数筛选工单",
    version="0.1.0"
)

tickets = [
    {
        "id": 101,
        "title": "API 登录失败",
        "status": "open"
    },
    {
        "id": 102,
        "title": "API 修改发票",
        "status": "in_progress"
    },
    {
        "id": 103,
        "title": "支付失败",
        "status": "open"
    },
    {
        "id": 104,
        "title": "导出报表失败",
        "status": "done"
    }
]


@app.get("/health")
def get_health():
    return {
        "status": "ok"
    }


@app.get("/")
def get_home():
    return {
        "message": "Day 76 FastAPI server is running"
    }


@app.get("/tickets")
def get_tickets(
    status: Literal["open", "in_progress", "done"] | None = None,
    limit: int = Query(
        default=10,
        ge=1,
        le=100
    )
):
    filtered_tickets = []

    for ticket in tickets:
        if status is None or ticket["status"] == status:
            filtered_tickets.append(ticket)

    return filtered_tickets[:limit]


@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: int = Path(ge=1)):
    return {
        "ticket_id": ticket_id
    }
