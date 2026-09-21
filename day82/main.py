from typing import Literal

from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field

from day82.ticket_service import (
    create_new_ticket,
    delete_ticket_by_id,
    find_ticket_by_id,
    list_tickets,
    update_ticket_by_id,
)


class TicketCreate(BaseModel):
    title: str = Field(min_length=1)


class TicketUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    status: Literal["open", "in_progress", "done"] | None = None


class Ticket(BaseModel):
    id: int
    title: str
    status: Literal["open", "in_progress", "done"]


app = FastAPI(
    title="工单系统 API",
    description="Day 82：分离接口层、业务层和数据层",
    version="0.1.0",
)


@app.get("/health")
def get_health():
    return {
        "status": "ok"
    }


@app.get("/")
def get_home():
    return {
        "message": "Day 82 FastAPI server is running"
    }


@app.get(
    "/tickets",
    response_model=list[Ticket],
)
def get_tickets(
    status: Literal["open", "in_progress", "done"] | None = None,
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
):
    return list_tickets(
        status,
        limit,
    )


@app.post(
    "/tickets",
    response_model=Ticket,
    status_code=201,
)
def create_ticket(ticket_to_create: TicketCreate):
    created_ticket = create_new_ticket(
        ticket_to_create.title
    )

    return created_ticket


@app.patch(
    "/tickets/{ticket_id}",
    response_model=Ticket,
    responses={
        404: {
            "description": "工单不存在"
        }
    },
)
def update_ticket(
    ticket_to_update: TicketUpdate,
    ticket_id: int = Path(ge=1),
):
    update_data = ticket_to_update.model_dump(
        exclude_unset=True,
        exclude_none=True,
    )

    updated_ticket = update_ticket_by_id(
        ticket_id,
        update_data,
    )

    if updated_ticket is None:
        raise HTTPException(
            status_code=404,
            detail="工单不存在",
        )

    return updated_ticket


@app.delete(
    "/tickets/{ticket_id}",
    status_code=204,
    responses={
        404: {
            "description": "工单不存在"
        }
    },
)
def delete_ticket(ticket_id: int = Path(ge=1)):
    deleted_ticket = delete_ticket_by_id(ticket_id)

    if deleted_ticket is None:
        raise HTTPException(
            status_code=404,
            detail="工单不存在",
        )

    return


@app.get(
    "/tickets/{ticket_id}",
    response_model=Ticket,
    responses={
        404: {
            "description": "工单不存在"
        }
    },
)
def get_ticket(ticket_id: int = Path(ge=1)):
    ticket = find_ticket_by_id(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="工单不存在",
        )

    return ticket
