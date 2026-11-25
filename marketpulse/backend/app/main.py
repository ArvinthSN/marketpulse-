from fastapi import FastAPI
from app.api.v1.routes import router
from app.database.session import engine
from app.database.session import Base
from app.services.health_service import database_health
from app.api.v1.analytics.routes import router as analytics_router
from app.api.v1.market.routes import router as market_router
import app.models.entities

app = FastAPI(title='MARKETPULSE', version='0.1.0')
app.include_router(router, prefix='/api/v1')
app.include_router(analytics_router, prefix='/api/v1')
app.include_router(market_router, prefix='/api/v1')


@app.on_event('startup')
def startup():
    pass


@app.get('/health')
def health(): return {'status':'ok'}


@app.get('/health/database')
def database_health_endpoint():
    if not database_health(): return {'status':'error','database':False}
    return {'status':'ok','database':True}


@app.get('/health/providers')
def provider_health():
    return {'status':'configured','providers':['yahoo'],'streaming':False}


@app.get('/health/live')
async def live_health():
    from app.market_data.services import live_state
    from app.core.config import settings
    if live_state.redis_manager is None:
        live_state.initialize(settings)
    redis_ok = await live_state.redis_manager.health_check()
    return {'status': 'ok' if redis_ok else 'degraded', 'redis': redis_ok,
            'provider_configured': settings.market_data_provider != 'none'}


@app.get('/health/ready')
async def ready_health():
    database_ok = database_health()
    return {'status': 'ready' if database_ok else 'not_ready', 'database': database_ok}
