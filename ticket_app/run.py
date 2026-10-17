import logging

import uvicorn

from ticket_app.config import settings

if __name__ == "__main__":
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s|%(levelname)s|%(name)s|%(message)s",
        datefmt="%H:%M:%S",
    )

    uvicorn.run(
        "ticket_app.main:app",
        host="127.0.0.1",
        port=settings.port,
        log_level=settings.log_level,
    )
