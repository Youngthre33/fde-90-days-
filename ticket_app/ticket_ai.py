"""后端 Python：把工单文字交给 AI，逐段取回文字，再检查完整建议的格式。"""

# 阅读路线：main.py 传入工单文字 → A2～A8 逐段交出文字 → A10 检查完整建议。
# 这里收到的 AI 平台消息，与 main.py 发给网页的 preview/done 消息是两层。
import json

import httpx
from pydantic import BaseModel, Field

from ticket_app.config import settings


# A1：先写好完整建议的格式要求；真正执行检查的位置在下面 A10。
class TicketAdvice(BaseModel):
    # summary 要有文字；两个列表各最多 3 项，每一项应是字符串。
    # 最多 3 项不等于必须有 3 项，空列表也符合这里的数量要求。
    summary: str = Field(min_length=1)
    next_steps: list[str] = Field(max_length=3)
    missing_info: list[str] = Field(max_length=3)


# A2：接收 main.py 整理好的工单文字，如“标题：打印机无法连接\n状态：open”。
# 参数后的 : str 是类型提示，本身不负责转换或检查实际传入值。
def stream_ticket_advice(ticket_text: str):
    # 没有平台凭据就报错；不继续发送这个请求，也不把凭据写进提示文字。
    if not settings.ai_api_key:
        raise ValueError("请先配置 TICKET_AI_API_KEY")

    # A3：给 AI 两条消息：system 说明怎么做，user 放本次工单资料。
    # 这些要求会指导 AI 输出；最终仍由 A10 检查，不能只凭提示语认定格式正确。
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
        {"role": "user", "content": ticket_text},  # 这里放真正传进来的工单文字。
    ]

    # 暂时不知道 AI 为什么结束；后面从平台消息里取到原因再保存。
    finish_reason = None

    # A4：后端连接 AI 平台，边收到边读；with 离开时会关闭这次响应。
    # response 保存平台的响应，后面的 for 从这个响应中逐行取内容。
    with httpx.stream(
        "POST",
        "https://api.deepseek.com/chat/completions",
        headers={"Authorization": f"Bearer {settings.ai_api_key}"},
        json={
            "model": "deepseek-flash",
            "messages": messages,  # 发送 A3 准备好的两条消息。
            "response_format": {"type": "json_object"},  # 要求建议文字采用 JSON 格式。
            "thinking": {"type": "disabled"},  # 关闭模型的思考模式。
            "stream": True,  # 请平台陆续发送内容，不等全部生成后才一次返回。
            "max_tokens": 800,  # 限制生成长度；token 不是“汉字个数”。
        },
        # 网络连接/读取等阶段的等待超时设置，不是“整次生成必须在 60 秒内结束”。
        timeout=60.0,
    ) as response:
        # HTTP 状态不成功时直接报错，由 main.py 的错误处理接住。
        response.raise_for_status()

        # A5：平台一行行发送文字；这里只处理以 data: 开头的消息行。
        for line in response.iter_lines():
            if not line.startswith("data:"):
                # 空行、注释等跳过；只跳过本轮，不结束整个读取过程。
                continue

            # 去掉前 5 个字符 data:，再去掉两端空白；结果交给 payload。
            # 例如 data: {"choices": [...]} → {"choices": [...]}（仍是文字）。
            payload = line[5:].strip()

            # A6：[DONE] 是平台发来的“消息发完了”，不是建议内容，也不是 JSON。
            # 必须先判断它，不能把 [DONE] 交给下面的 json.loads。
            if payload == "[DONE]":
                # 发完了不一定是完整答案；如因长度上限结束，原因就不是 stop。
                if finish_reason != "stop":
                    raise ValueError("AI建议未完整生成，请重试")
                # 确认正常结束，结束这个函数；上层的 for 因而读完，随后检查完整建议。
                return

            # A7：把这一条平台消息的 JSON 文字读成 Python 字典，交给 data。
            # 这是外层消息；其中 delta.content 仍可能只是建议 JSON 的一小段文字。
            data = json.loads(payload)
            if "error" in data:
                raise ValueError("AI生成失败，请重试")

            usage = data.get("usage")
            if usage is not None:
                 cost = estimate_ticket_advice_cost(usage)




            # choices 是平台规定的字段。缺少时先取 []；没有候选项就等下一行。
            choices = data.get("choices", [])
            if not choices:
                continue

            # 取第一项；这里的 [0] 是列表里的第一个位置。
            choice = choices[0]
            if choice.get("finish_reason") is not None:
                # 有明确结束原因才更新；中间消息中的 None 不覆盖之前保存的值。
                finish_reason = choice["finish_reason"]

            # delta 中的 content 是这次新增的文字；没有该字段时 get 得到 None。
            # 它不保证是完整建议，也不同于 main.py 循环中累计拼接后的 content。
            part = choice["delta"].get("content")
            if part:
                # 把这一小段交给上层 for 的 part 接住，然后暂停在这里。
                # 上层要求下一段时，从这里继续；yield 不会直接把文字画到网页上。
                yield part

    # A8：若没有通过 A6 的正常 return 就读到了连接末尾，不能假装生成成功。
    raise ValueError("AI生成连接提前结束，请重试")


# A10：完整建议检查。main.py 在收齐所有片段后，把完整字符串传到这里。
# : str / -> dict 只是输入、返回类型提示；真正的转换和检查是下面三行。
def parse_ticket_advice(content: str) -> dict:
    # 建议 JSON 字符串 → 字典。例如 '{"summary":"打印机", ...}' → {...}。
    # 这里只读出文字里原本写好的结构，不会把错误的字段自动排成正确格式。
    data = json.loads(content)
    # 按 A1 检查字段和类型；通过后得到 TicketAdvice 对象，失败就报错交给上层。
    advice = TicketAdvice.model_validate(data)
    # 检查后的对象 → 普通字典，return 把字典交回 main.py 的 advice 接住。
    return advice.model_dump()
