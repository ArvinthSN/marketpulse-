from datetime import datetime
from pydantic import BaseModel


class CountryResponse(BaseModel):
    code: str; name: str; currency: str; timezone: str


class ExchangeResponse(BaseModel):
    code: str; name: str; country_code: str; yahoo_suffix: str | None; currency: str; timezone: str; enabled: bool


class CompanyResponse(BaseModel):
    id: int; name: str; country_code: str | None; website: str | None = None


class HistoryResponse(BaseModel):
    timestamp: datetime; open: float; high: float; low: float; close: float; volume: int; currency: str


class IngestionRunResponse(BaseModel):
    id: int; scope_type: str; scope_value: str | None; status: str; period: str | None; interval: str | None
    successful: int; failed: int; inserted: int; updated: int; rejected: int
    started_at: datetime; finished_at: datetime | None; error_summary: str | None
