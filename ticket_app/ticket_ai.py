import httpx
import json

from ticket_app.config import settings
from pydantic import BaseModel, Field

class TicketAdvice(BaseModel):
    summary: str = Field(min_length=1)
    next_steps: list[str] = Field(max_length=3)
    missing_info: list[str] = Field(max_length=3)


def generate_ticket_advice(ticket_text: str) ->str:
    if not settings.ai_api_key:
        raise ValueError("请先配置 TICKET_AI_API_KEY")

    messages = [
        {
            "role": "system",
            "content": (
                "你是工单助手，输入资料是工单的标题和状态。\n"
                "任务：概括问题，给出可由工作人员执行的下一步建议。\n"
                "约束：摘要只写已知事实；未知原因写“待确认”，不要编造。\n"
                "不要声称已联系客户、解决问题或修改工单。\n"
                "输出：只返回一个 JSON 对象，内容用中文，不要附加说明或代码块。\n"
                "字段要求：summary 是字符串；next_steps 和 missing_info 是字符串数组。\n"
                "summary 最多2句；两个数组各最多3项。\n"
                '格式示例：{"summary":"摘要",'
                '"next_steps":["建议"],'
                '"missing_info":["待补充信息"]}。\n'
                "示例只说明格式，请根据本次工单填写实际内容。"
            ),
        },
        {"role": "user", "content": ticket_text},
    ]
    response = httpx.post(
        "https://api.deepseek.com/chat/completions",
        headers={"Authorization": f"Bearer {settings.ai_api_key}"},
        json={
            "model": "deepseek-flash",
            "messages": messages,
            "response_format":{"type":"json_object"},
            "thinking": {"type": "disabled"},
            "stream": False,
            "max_tokens": 800,
        },
        timeout=60.0,
    )

    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def parse_ticket_advice(content: str) -> dict:
    data = json.loads(content)
    advice = TicketAdvice.model_validate(data)
    return advice.model_dump()