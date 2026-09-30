import re
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest
from psycopg import sql

from ticket_app import ticket_repository
from ticket_app.config import settings


def connect_to_database():
    return psycopg.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        connect_timeout=5,
    )


# 每例在当前数据库中建立独立schema，不读写public中的真实工单表。
@pytest.fixture(autouse=True)
def isolated_database(monkeypatch):

    if settings.db_name != "ticket_app_test":
        raise RuntimeError("测试只允许连接 ticket_app_test")
    if not settings.db_password:
        pytest.skip(
            "PostgreSQL测试未运行：请先在ticket_app/.env配置TICKET_DB_PASSWORD。"
        )

    schema_name = f"ticket_app_test_{uuid4().hex}"
    schema_path = Path(ticket_repository.__file__).resolve().parent / "schema.sql"

    def connect_to_test_schema():
        connection = connect_to_database()
        try:
            connection.execute(
                sql.SQL("SET search_path TO {}").format(sql.Identifier(schema_name))
            )
            connection.commit()
        except BaseException:
            connection.close()
            raise
        return connection

    with connect_to_database() as connection:
        connection.execute(
            sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema_name))
        )

    try:
        with connect_to_test_schema() as connection:
            connection.execute(schema_path.read_text(encoding="utf-8"))

        monkeypatch.setattr(
            ticket_repository,
            "get_connection",
            connect_to_test_schema,
        )
        yield connect_to_test_schema
    finally:
        # 仅清理本例生成的完整随机名称，绝不删除public或其他schema。
        if re.fullmatch(r"ticket_app_test_[0-9a-f]{32}", schema_name) is None:
            raise RuntimeError("拒绝清理不符合测试命名规则的schema")
        with connect_to_database() as connection:
            connection.execute(
                sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema_name))
            )
