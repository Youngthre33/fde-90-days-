from typing import Literal

from fastapi import FastAPI, HTTPException, Path, Query

from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    title: str = Field(min_length=1)


app = FastAPI(
    title="工单系统 API",
    description="Day 78：通过请求正文创建工单",
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
        "message": "Day 78 FastAPI server is running"
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


@app.post(
    "/tickets",
    status_code=201
)
def create_ticket(ticket_to_create: TicketCreate):
    created_ticket = {
        "id": tickets[-1]["id"] + 1,
        "title": ticket_to_create.title,
        "status": "open"
    }

    tickets.append(created_ticket)

    return created_ticket


@app.get(
    "/tickets/{ticket_id}",
    responses={
        404: {
            "description": "工单不存在"
        }
    }
)
def get_ticket(ticket_id: int = Path(ge=1)):
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket
    raise HTTPException(
        status_code=404,
        detail="工单不存在"
    )
