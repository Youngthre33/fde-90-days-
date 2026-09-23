import logging
from time import perf_counter
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Path, Query, Request
from pydantic import BaseModel, Field

from day82.ticket_service import (
    create_new_ticket,
    delete_ticket_by_id,
    find_ticket_by_id,
    list_tickets,
    update_ticket_by_id,
)

logger = logging.getLogger(__name__)


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
    description="Day 87: 记录工单操作日志",
    version="0.1.0",
)


@app.middleware("http")
async def log_request(request: Request, call_next):
    request_id = uuid4().hex
    request.state.request_id = request_id

    start_time = perf_counter()

    logger.info(
        "请求开始，request_id=%s, method=%s, url=%s",
        request_id,
        request.method,
        request.url.path,
    )

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (perf_counter() - start_time) * 1000

        logger.exception(
            "请求发生异常，request_id=%s, method=%s, path=%s, duration_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            duration_ms,
        )

        raise

    duration_ms = (perf_counter() - start_time) * 1000

    logger.info(
        "请求结束，request_id=%s, status=%s, duration_ms=%.2f",
        request_id,
        response.status_code,
        duration_ms,
    )

    response.headers["X-Request-ID"] = request_id

    return response


@app.get("/health")
def get_health():
    return {
        "status": "ok"
    }


@app.get("/")
def get_home():
    return {
        "message": "Day 87 FastAPI server is running"
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
def get_ticket(
    request: Request,
    ticket_id: int = Path(ge=1),
):
    request_id = request.state.request_id

    logger.info(
        "查询工单开始, request_id=%s, ticket_id=%s",
        request_id,
        ticket_id,
    )

    ticket = find_ticket_by_id(ticket_id)

    if ticket is None:
        logger.warning(
            "查询工单失败, request_id=%s, ticket_id=%s",
            request_id,
            ticket_id,
        )
        raise HTTPException(
            status_code=404,
            detail="工单不存在",
        )

    logger.info(
        "查询工单成功, request_id=%s, ticket_id=%s",
        request_id,
        ticket_id,
    )

    return ticket
