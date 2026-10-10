import httpx

from ticket_app.config import settings

def generate_ticket_advice(ticket_text: str) ->str:
    if not settings.ai_api_key:
        raise ValueError("请先配置 TICKET_AI_API_KEY")


    messages = [

        {"role":"system", "content": "你是工单助手, 用中文给出工单摘要和建议下一步, 不要声称已执行操作,"},

        {"role": "user", "content": ticket_text }, ]

    
    response = httpx.post(
        "https://api.deepseek.com/chat/completions",
        headers={"Authorization": f"Bearer {settings.ai_api_key}"},
        json={
            "model": "deepseek-flash",
            "messages": messages,
            "thinking": {"type": "disabled"},
            "stream": False,
            "max_tokens": 800,
        },
        timeout=60.0,
    )

    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]