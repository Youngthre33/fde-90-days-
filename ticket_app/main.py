import logging
from time import perf_counter
from typing import Literal
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Path, Query, Request
from pydantic import BaseModel, Field

from ticket_app.ticket_service import (
    create_new_ticket,
    delete_ticket_by_id,
    find_ticket_by_id,
    list_ticket_events,
    list_tickets,
    update_ticket_by_id,
)


from ticket_app.auth import get_role, require_admin

from fastapi.staticfiles import StaticFiles

from fastapi.responses import StreamingResponse

from ticket_app.ticket_ai import (
    parse_ticket_advice,
    stream_ticket_advice,
)

import json
from pydantic_core import from_json




logger = logging.getLogger(__name__)

# Day159：本后端进程暂存检查合格的完整建议；重启后清空。
# 键是完整的工单输入文字，值是最终建议字典；不保存预览或错误。
advice_cache = {}


class TicketCreate(BaseModel):
    title: str = Field(min_length=1, pattern=r"\S")


class TicketUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, pattern=r"\S")
    status: Literal["open", "in_progress", "done"] | None = None


class Ticket(BaseModel):
    id: int
    title: str
    status: Literal["open", "in_progress", "done"]


class TicketEvent(BaseModel):
    id: int
    ticket_id: int
    note: str


app = FastAPI(
    title="工单系统 API",
    description="工单项目：数据库、分页与处理记录",
    version="0.1.0",
)

app.mount(
    "/web",
    StaticFiles(directory="ticket_app/web", html=True),
    name="web",
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
        "message": "ticket_app server is running"
    }


@app.get(
    "/tickets",
    response_model=list[Ticket],
    dependencies=[Depends(get_role)],
)
def get_tickets(
    status: Literal["open", "in_progress", "done"] | None = None,
    limit: int = Query(default=10, ge=1, le=100),
    page: int = Query(default=1, ge=1, le=1_000_000),
    order: Literal["asc", "desc"] = "asc",
):
    return list_tickets(
        status=status,
        limit=limit,
        page=page,
        order=order,
    )



@app.get(
    "/tickets/{ticket_id}/events",
    response_model=list[TicketEvent],
    dependencies=[Depends(get_role)],
    responses={404: {"description": "工单不存在"}},
)
def get_ticket_events(ticket_id: int = Path(ge=1)):
    events = list_ticket_events(ticket_id)

    if events is None:
        raise HTTPException(status_code=404, detail="工单不存在")

    return events


















@app.post(
    "/tickets",
    response_model=Ticket,
    dependencies=[Depends(get_role)],
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
    dependencies=[Depends(get_role)],
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
    dependencies=[Depends(require_admin)],
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
    dependencies=[Depends(get_role)],
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



def stream_advice_events(ticket_text: str):
    chunks = []

    try:
        # C1：当前权限和工单查询已由路由完成，再按完整输入找旧建议。
        cached_advice = advice_cache.get(ticket_text)
        if cached_advice is not None:
            logger.info("AI建议缓存命中，复用完整建议；本次未调用模型")
            message = {"type": "done", "data": cached_advice}
            text = json.dumps(message, ensure_ascii=False)
            line = text + "\n"
            yield line
            return

        # C2：没有对应的完整建议，继续走原来的 AI 生成和预览流程。
        logger.info("AI建议缓存未命中，开始生成")

        for part in stream_ticket_advice(ticket_text):
            chunks.append(part)
            content = "".join(chunks)

            try:
                preview = from_json(content,allow_partial= "trailing-strings")

            except ValueError:
                continue

            if not isinstance(preview, dict):
                continue

            message = {"type": "preview", "data": preview}
            text = json.dumps(message, ensure_ascii=False)
            line = text + "\n"
            yield line

        content = "".join(chunks)
        advice = parse_ticket_advice(content)
        message = {"type": "done", "data": advice}
        text = json.dumps(message, ensure_ascii=False)
        line = text + "\n"
        # C3：完整内容检查、消息准备都成功后，保存供下次复用。
        advice_cache[ticket_text] = advice
        yield line ###这里就输出###

    except Exception:
        # B5：记录错误，交出失败消息
        logger.exception("AI建议生成失败")
        message = {"type": "error", "message": "AI建议生成失败，请重试"}
        text = json.dumps(message, ensure_ascii=False)
        line = text + "\n"
        yield line



@app.post(
    "/tickets/{ticket_id}/advice/stream",
    dependencies=[Depends(get_role)],
)
def create_ticket_advice_stream(ticket_id: int = Path(ge=1)):
    ticket = find_ticket_by_id(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="工单不存在")

    ticket_text = (
        f"标题：{ticket['title']}\n"
        f"状态：{ticket['status']}"
    )

    return StreamingResponse(
        stream_advice_events(ticket_text),
        media_type="application/x-ndjson",
    )
