from zoneinfo import ZoneInfo
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.entities import Country, Exchange
from app.registry.definitions import COUNTRIES, EXCHANGES


def validate_registry() -> None:
    for country in COUNTRIES:
        if len(country.code) != 2 or not country.code.isupper():
            raise ValueError(f'Invalid ISO country code: {country.code}')
        if len(country.currency) != 3 or not country.currency.isupper():
            raise ValueError(f'Invalid currency: {country.currency}')
        ZoneInfo(country.timezone)
    for exchange in EXCHANGES:
        if exchange.country_code not in {c.code for c in COUNTRIES}:
            raise ValueError(f'Unknown country for exchange {exchange.code}')
        ZoneInfo(exchange.timezone)


def sync_registry(db: Session) -> tuple[int, int]:
    validate_registry()
    country_count = exchange_count = 0
    for definition in COUNTRIES:
        country = db.scalar(select(Country).where(Country.code == definition.code))
        if country is None:
            db.add(Country(code=definition.code, name=definition.name, currency=definition.currency, timezone=definition.timezone))
            country_count += 1
        else:
            country.name, country.currency, country.timezone = definition.name, definition.currency, definition.timezone
    db.flush()
    for definition in EXCHANGES:
        exchange = db.scalar(select(Exchange).where(Exchange.code == definition.code))
        values = dict(name=definition.name, country_code=definition.country_code, yahoo_suffix=definition.yahoo_suffix,
                       currency=definition.currency, timezone=definition.timezone, enabled=definition.enabled)
        if exchange is None:
            db.add(Exchange(code=definition.code, **values)); exchange_count += 1
        else:
            for key, value in values.items(): setattr(exchange, key, value)
    db.commit()
    return country_count, exchange_count
