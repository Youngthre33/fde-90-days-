from fastapi import FastAPI


app = FastAPI(
    title="工单系统 API",
    description="Day 74：第一个 FastAPI 应用",
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
        "message": "Day 74 FastAPI server is running"
    }
