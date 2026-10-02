FROM python:3.12-slim
WORKDIR /app
COPY ticket_app/requirements.txt /app/requirements.txt
RUN python -m pip install  --no-cache-dir  -r requirements.txt
COPY ticket_app/ /app/ticket_app/
CMD [ "python","-m","uvicorn","ticket_app.main:app","--host","0.0.0.0","--port", "8001"]