import logging

import uvicorn

from day86.config import settings

if __name__ == "__main__":
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s|%(levelname)s|%(name)s|%(message)s",
        datefmt="%H:%M:%S",
    )

    uvicorn.run(
        "day88.main:app",
        host="127.0.0.1",
        port=settings.port,
        log_level=settings.log_level,
    )
