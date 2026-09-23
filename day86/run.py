import uvicorn

from day86.config import settings


if __name__ == "__main__":
    uvicorn.run(
        "day82.main:app",
        host="127.0.0.1",
        port=settings.port,
        log_level=settings.log_level,
    )
