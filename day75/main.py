from fastapi import FastAPI, Path


app = FastAPI(
    title="工单系统 API",
    description="Day 75：使用路径参数读取工单 ID",
    version="0.1.0"
)


@app.get("/health")
def get_health():
    return {
        "status": "ok"
    }


@app.get("/")
def get_home():
    return {
        "message": "Day 75 FastAPI server is running"
    }


@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: int = Path(ge=1)):
    return {
        "ticket_id": ticket_id
    }
