from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.security import require_admin
from app.models.entities import Country, Exchange, Company, CompanySymbol, HistoricalPrice, IngestionRun
from app.schemas.responses import CountryResponse, ExchangeResponse, CompanyResponse, HistoryResponse, IngestionRunResponse
from app.schemas.requests import IngestionRequest
from app.services.ingestion_service import IngestionService
from app.ingestion.providers.yahoo_provider import YahooProvider

router = APIRouter()


@router.get('/countries', response_model=list[CountryResponse])
def countries(db: Session = Depends(get_db)):
    return db.scalars(select(Country).order_by(Country.code)).all()


@router.get('/exchanges', response_model=list[ExchangeResponse])
def exchanges(country: str | None = None, db: Session = Depends(get_db)):
    stmt = select(Exchange).order_by(Exchange.code)
    if country: stmt = stmt.where(Exchange.country_code == country.upper())
    return db.scalars(stmt).all()


@router.get('/countries/{country_code}/exchanges', response_model=list[ExchangeResponse])
def country_exchanges(country_code: str, db: Session = Depends(get_db)):
    code = country_code.upper()
    country = db.scalar(select(Country).where(Country.code == code))
    if country is None:
        raise HTTPException(status_code=404, detail='Country not found')
    return db.scalars(select(Exchange).where(Exchange.country_code == code).order_by(Exchange.code)).all()


@router.get('/companies', response_model=list[CompanyResponse])
def companies(country: str | None = None, exchange: str | None = None, limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    stmt = select(Company)
    if country: stmt = stmt.where(Company.country_code == country.upper())
    if exchange:
        exchange_row = db.scalar(select(Exchange).where(Exchange.code == exchange.upper()))
        if exchange_row:
            stmt = stmt.join(CompanySymbol, CompanySymbol.company_id == Company.id).where(CompanySymbol.exchange_id == exchange_row.id)
    stmt = stmt.order_by(Company.id).limit(limit).offset(offset)
    return db.scalars(stmt).unique().all()


@router.get('/companies/{company_id}', response_model=CompanyResponse)
def company(company_id: int, db: Session = Depends(get_db)):
    row = db.get(Company, company_id)
    if row is None: raise HTTPException(404, 'Company not found')
    return row


@router.get('/companies/{company_id}/history', response_model=list[HistoryResponse])
def company_history(company_id: int, limit: int = Query(1000, ge=1, le=10000), db: Session = Depends(get_db)):
    stmt = select(HistoricalPrice).join(CompanySymbol, CompanySymbol.id == HistoricalPrice.company_symbol_id).where(CompanySymbol.company_id == company_id).order_by(HistoricalPrice.timestamp.desc()).limit(limit)
    return db.scalars(stmt).all()


@router.post('/ingestion/run', response_model=IngestionRunResponse, dependencies=[Depends(require_admin)])
def run_ingestion(request: IngestionRequest, db: Session = Depends(get_db)):
    if not request.exchange_code:
        raise HTTPException(status_code=422, detail='Exchange_code is required in Phase 1.1 unless a configured instrument import is specified')
    try:
        return IngestionService(db, YahooProvider()).run_exchange(request.exchange_code, request.limit, request.period, request.interval)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get('/ingestion/runs', response_model=list[IngestionRunResponse])
def ingestion_runs(limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    return db.scalars(select(IngestionRun).order_by(IngestionRun.started_at.desc()).limit(limit)).all()


@router.get('/ingestion/runs/{run_id}', response_model=IngestionRunResponse)
def ingestion_run(run_id: int, db: Session = Depends(get_db)):
    row = db.get(IngestionRun, run_id)
    if row is None: raise HTTPException(404, 'Ingestion run not found')
    return row


@router.post('/ingestion/runs/{run_id}/resume', response_model=IngestionRunResponse, dependencies=[Depends(require_admin)])
def resume_ingestion(run_id: int, db: Session = Depends(get_db)):
    try:
        return IngestionService(db, YahooProvider()).resume_run(run_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
