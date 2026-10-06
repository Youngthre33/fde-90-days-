from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from ticket_app.config import settings
from secrets import compare_digest

berarer_scheme = HTTPBearer()


def read_token( credentials=Depends(berarer_scheme)):
    return credentials.credentials

def get_role(token=Depends(read_token)):
    if not settings.staff_token or not settings.admin_token:
        raise HTTPException(status_code=503, detail="访问凭据尚未配置")

    if settings.staff_token == settings.admin_token:
        raise HTTPException(status_code=503, detail="两种身份的Token不能相同")

    token_bytes = token.encode("utf-8")
    staff_bytes = settings.staff_token.encode("utf-8")
    admin_bytes = settings.admin_token.encode("utf-8")

    if compare_digest(token_bytes, staff_bytes):
        return "staff"

    if compare_digest(token_bytes, admin_bytes):
        return "admin"

    raise HTTPException(
        status_code=401,
        detail= "访问凭据无效",
        headers={"WWW-Authenticate":"Bearer"}
    )


def require_admin(role=Depends(get_role)):
    if role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")

    return role
    
    