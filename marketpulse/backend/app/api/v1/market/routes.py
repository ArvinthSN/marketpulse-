from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.config import settings
from app.market_data.services.live_market_service import LiveMarketService
from app.market_data.services.subscription_service import SubscriptionService
from app.market_data.services.market_session_service import MarketSessionService
from app.market_data.services import live_state


router = APIRouter(prefix='/market', tags=['live-market'])


def cache():
    if live_state.quote_cache is None:
        live_state.initialize(settings)
    return live_state.quote_cache


@router.get('/quotes')
async def quotes(symbols: str = Query(..., min_length=1), exchange: str = 'NASDAQ', db: Session = Depends(get_db)):
    symbol_list = [symbol.strip().upper() for symbol in symbols.split(',') if symbol.strip()]
    try:
        symbol_list = SubscriptionService.validate(symbol_list)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return await LiveMarketService(db, cache()).get_quotes(symbol_list[:settings.market_data_max_subscriptions], exchange)


@router.get('/quotes/{symbol}')
async def quote(symbol: str, exchange: str = 'NASDAQ', db: Session = Depends(get_db)):
    try:
        symbol = SubscriptionService.validate([symbol])[0]
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    result = await LiveMarketService(db, cache()).get_quote(symbol, exchange)
    if result is None:
        raise HTTPException(status_code=404, detail='Quote unavailable')
    return result


@router.get('/status')
async def market_status(exchange: str = 'NASDAQ'):
    return {'exchange': exchange.upper(), 'status': 'UNAVAILABLE',
            'provider_configured': bool(settings.market_data_provider and settings.market_data_provider != 'none')}


@router.get('/providers/health')
async def provider_health():
    from app.market_data.providers.provider_factory import ProviderFactory
    provider = ProviderFactory.create()
    return await provider.health_check()


@router.get('/exchanges/{exchange_code}/status')
async def exchange_status(exchange_code: str):
    return {'exchange': exchange_code.upper(), 'status': 'UNAVAILABLE',
            'timezone': 'exchange_registry_required', 'source': 'market_session_not_configured'}


@router.get('/universe')
async def universe(db: Session = Depends(get_db)):
    from app.models.entities import InstrumentUniverse
    rows = db.query(InstrumentUniverse).filter(InstrumentUniverse.active.is_(True)).limit(1000).all()
    return {'items': [{'symbol': row.normalized_symbol, 'exchange_id': row.exchange_id,
                       'source': row.source, 'active': row.active} for row in rows],
            'total': len(rows), 'coverage': 'maintained_import_or_provider_discovery'}


@router.websocket('/live')
async def live_websocket(websocket: WebSocket, token: str | None = None):
    if settings.market_data_api_key and token != settings.market_data_api_key:
        await websocket.close(code=1008, reason='Unauthorized')
        return
    if live_state.connection_manager is None:
        live_state.initialize(settings)
    if not await live_state.connection_manager.connect(websocket):
        return
    try:
        while True:
            message = await websocket.receive_json()
            action = str(message.get('action') or '').lower()
            if action == 'ping':
                await websocket.send_json({'event': 'pong'})
            elif action in {'subscribe', 'unsubscribe'}:
                symbols = message.get('symbols')
                if not isinstance(symbols, list) or len(symbols) > settings.market_data_max_subscriptions:
                    await websocket.send_json({'event': 'error', 'message': 'Invalid subscription list'})
                    continue
                try:
                    symbols = SubscriptionService.validate(symbols)
                except ValueError as exc:
                    await websocket.send_json({'event': 'error', 'message': str(exc)})
                    continue
                if action == 'subscribe':
                    live_state.connection_manager.subscribe(websocket, symbols)
                    for symbol in symbols:
                        await websocket.send_json({'event': 'subscribed', 'symbol': symbol})
                else:
                    live_state.connection_manager.unsubscribe(websocket, symbols)
                    await websocket.send_json({'event': 'unsubscribed', 'symbols': symbols})
            else:
                await websocket.send_json({'event': 'error', 'message': 'Unsupported action'})
    except WebSocketDisconnect:
        pass
    finally:
        live_state.connection_manager.disconnect(websocket)
