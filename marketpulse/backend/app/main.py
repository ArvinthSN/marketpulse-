from fastapi import FastAPI
from app.api.v1.routes import router
from app.database.session import engine
from app.database.session import Base
from app.services.health_service import database_health
import app.models.entities

app = FastAPI(title='MARKETPULSE', version='0.1.0')
app.include_router(router, prefix='/api/v1')


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
