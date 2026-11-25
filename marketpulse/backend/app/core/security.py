from fastapi import Header, HTTPException, status
from app.core.config import settings


def require_admin(x_api_key: str | None = Header(default=None)) -> None:
    if x_api_key != settings.admin_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid or missing administrative API key')
