from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.security import require_admin
from app.analytics.repositories.analytics_repository import AnalyticsRepository
from app.analytics.services.company_analytics import CompanyAnalyticsService
from app.analytics.services.sector_analytics import SectorAnalyticsService
from app.analytics.services.country_analytics import CountryAnalyticsService
from app.analytics.services.global_analytics import GlobalAnalyticsService
from app.analytics.services.ranking_service import RankingService
from app.analytics.tasks.analytics_jobs import AnalyticsJobService
from app.models.entities import AnalyticsJobRun, Country


router = APIRouter(prefix='/analytics', tags=['analytics'])


@router.get('/global/overview')
def global_overview(period: str = '1D', reporting_currency: str = 'USD', db: Session = Depends(get_db)):
    repository = AnalyticsRepository(db)
    return GlobalAnalyticsService(repository).overview(period, reporting_currency.upper())


@router.get('/global/performance')
def global_performance(period: str = '1D', reporting_currency: str = 'USD', db: Session = Depends(get_db)):
    repository = AnalyticsRepository(db)
    return GlobalAnalyticsService(repository).overview(period, reporting_currency.upper())


@router.get('/global/countries')
def global_countries(reporting_currency: str = 'USD', limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    repository = AnalyticsRepository(db)
    countries = db.scalars(select(Country).order_by(Country.code).limit(limit).offset(offset)).all()
    service = CountryAnalyticsService(repository)
    return [item for country in countries if (item := service.overview(country.code, reporting_currency=reporting_currency.upper())) is not None]


@router.get('/global/sectors')
def global_sectors(reporting_currency: str = 'USD', limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    from app.models.entities import Sector
    sectors = db.scalars(select(Sector).order_by(Sector.id).limit(limit).offset(offset)).all()
    service = SectorAnalyticsService(AnalyticsRepository(db))
    return [item for sector in sectors if (item := service.overview(sector.id, reporting_currency=reporting_currency.upper())) is not None]


@router.get('/global/top-companies')
def global_top_companies(metric: str = 'market_cap', limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    if metric not in {'market_cap', 'volume'}:
        raise HTTPException(status_code=422, detail='metric must be market_cap or volume')
    repository = AnalyticsRepository(db)
    companies = repository.get_companies(limit=limit)
    items = [{'company_id': company.id, 'name': company.name, 'market_cap': float(company.market_cap) if company.market_cap is not None else None,
              'volume': None, 'currency': company.country_code or ''} for company in companies]
    if metric == 'market_cap':
        return RankingService.rank_market_caps(items, limit)
    if metric == 'volume':
        return RankingService.rank_volume(items, limit)
    raise HTTPException(status_code=422, detail='metric must be market_cap or volume')


@router.get('/global/market-breadth')
def global_market_breadth(period: str = '1D', db: Session = Depends(get_db)):
    result = GlobalAnalyticsService(AnalyticsRepository(db)).overview(period)
    return result['market_breadth']


@router.get('/countries/{country_code}/overview')
def country_overview(country_code: str, reporting_currency: str = 'USD', db: Session = Depends(get_db)):
    result = CountryAnalyticsService(AnalyticsRepository(db)).overview(country_code, reporting_currency=reporting_currency.upper())
    if result is None:
        raise HTTPException(status_code=404, detail='Country not found')
    return result


@router.get('/countries/{country_code}/performance')
def country_performance(country_code: str, period: str = '1D', reporting_currency: str = 'USD', db: Session = Depends(get_db)):
    return country_overview(country_code, reporting_currency, db)


@router.get('/countries/{country_code}/sectors')
def country_sectors(country_code: str, limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    from app.models.entities import Sector
    sectors = db.scalars(select(Sector).order_by(Sector.id).limit(limit)).all()
    service = SectorAnalyticsService(AnalyticsRepository(db))
    return [service.overview(sector.id) for sector in sectors]


@router.get('/countries/{country_code}/companies')
def country_companies(country_code: str, limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    repository = AnalyticsRepository(db)
    companies = repository.get_companies(country_code=country_code, limit=limit, offset=offset)
    service = CompanyAnalyticsService(repository)
    return [item for company in companies if (item := service.performance(company.id)) is not None]


@router.get('/countries/{country_code}/gainers')
def country_gainers(country_code: str, limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    repository = AnalyticsRepository(db)
    companies = repository.get_companies(country_code=country_code, limit=limit)
    items = []
    service = CompanyAnalyticsService(repository)
    for company in companies:
        performance = service.performance(company.id)
        if performance:
            value = performance['performance'].get('1D')
            if value is not None and value > 0:
                items.append({'company_id': company.id, 'name': company.name, 'return_percentage': value})
    return sorted(items, key=lambda item: item['return_percentage'], reverse=True)


@router.get('/countries/{country_code}/losers')
def country_losers(country_code: str, limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    repository = AnalyticsRepository(db)
    companies = repository.get_companies(country_code=country_code, limit=limit)
    items = []
    service = CompanyAnalyticsService(repository)
    for company in companies:
        performance = service.performance(company.id)
        if performance:
            value = performance['performance'].get('1D')
            if value is not None and value < 0:
                items.append({'company_id': company.id, 'name': company.name, 'return_percentage': value})
    return sorted(items, key=lambda item: item['return_percentage'])


@router.get('/sectors/{sector_id}/overview')
def sector_overview(sector_id: int, reporting_currency: str = 'USD', db: Session = Depends(get_db)):
    result = SectorAnalyticsService(AnalyticsRepository(db)).overview(sector_id, reporting_currency=reporting_currency.upper())
    if result is None:
        raise HTTPException(status_code=404, detail='Sector not found')
    return result


@router.get('/sectors/{sector_id}/companies')
def sector_companies(sector_id: int, limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    repository = AnalyticsRepository(db)
    companies = repository.get_companies(sector_id=sector_id, limit=limit, offset=offset)
    return [{'company_id': company.id, 'name': company.name, 'market_cap': float(company.market_cap) if company.market_cap is not None else None} for company in companies]


@router.get('/sectors/{sector_id}/performance')
def sector_performance(sector_id: int, period: str = '1D', reporting_currency: str = 'USD', db: Session = Depends(get_db)):
    return sector_overview(sector_id, reporting_currency, db)


@router.get('/companies/{company_id}/performance')
def company_performance(company_id: int, period: str = '1D', reporting_currency: str = 'USD', adjusted: bool = True, db: Session = Depends(get_db)):
    try:
        result = CompanyAnalyticsService(AnalyticsRepository(db)).performance(company_id, reporting_currency.upper(), period, adjusted)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    if result is None:
        raise HTTPException(status_code=404, detail='Company not found')
    return result


@router.get('/companies/{company_id}/metrics')
def company_metrics(company_id: int, volatility_window: int = Query(20, ge=2, le=365), volume_window: int = Query(20, ge=1, le=365), db: Session = Depends(get_db)):
    result = CompanyAnalyticsService(AnalyticsRepository(db)).metrics(company_id, volatility_window, volume_window)
    if result is None:
        raise HTTPException(status_code=404, detail='Company not found')
    return result


@router.get('/market-breadth')
def market_breadth(period: str = '1D', db: Session = Depends(get_db)):
    return GlobalAnalyticsService(AnalyticsRepository(db)).overview(period)['market_breadth']


@router.post('/jobs/run', dependencies=[Depends(require_admin)])
def run_analytics_job(scope_type: str = 'global', scope_value: str | None = None, periods: str = '1D', db: Session = Depends(get_db)):
    if scope_type not in {'global', 'country', 'exchange', 'sector'}:
        raise HTTPException(status_code=422, detail='Unsupported analytics scope')
    period_list = [period.strip().upper() for period in periods.split(',') if period.strip()]
    invalid = [period for period in period_list if period not in {'1D','1W','1M','3M','6M','YTD','1Y','3Y','5Y','ALL'}]
    if invalid:
        raise HTTPException(status_code=422, detail=f'Unsupported periods: {invalid}')
    job = AnalyticsJobService(db).start(scope_type, scope_value, period_list)
    repository = AnalyticsRepository(db)
    processed = len(repository.get_companies(limit=10000))
    return AnalyticsJobService(db).complete(job.id, records_processed=processed)


@router.get('/jobs/{job_id}')
def analytics_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(AnalyticsJobRun, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail='Analytics job not found')
    return job
