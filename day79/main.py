from typing import Literal

from fastapi import FastAPI, HTTPException, Path, Query

from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    title: str = Field(min_length=1)


class Ticket(BaseModel):
    id: int
    title: str
    status: Literal["open", "in_progress", "done"]

app = FastAPI(
    title="工单系统 API",
    description="Day 79：使用响应模型规定输出结构",
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
        "message": "Day 79 FastAPI server is running"
    }


@app.get(
    "/tickets",
    response_model=list[Ticket]
)
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
    response_model=Ticket,
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
    response_model=Ticket,
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
