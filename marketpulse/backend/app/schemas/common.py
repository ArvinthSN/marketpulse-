from pydantic import BaseModel, Field


class PaginatedResponse(BaseModel):
    items: list
    total: int
    limit: int
    offset: int
