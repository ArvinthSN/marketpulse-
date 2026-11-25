from app.api.v1.routes import companies
from app.models.entities import Country, Exchange, Sector, Company, CompanySymbol


def seed_company_search_data(db_session):
    db_session.add(Country(code='US', name='United States', currency='USD', timezone='America/New_York'))
    db_session.add(Exchange(code='NASDAQ', name='NASDAQ', country_code='US', currency='USD', timezone='America/New_York', enabled=True))
    db_session.add(Sector(id=1, name='Technology'))
    db_session.flush()
    first = Company(name='Apple Inc.', short_name='Apple', country_code='US', sector_id=1, isin='US0378331005')
    second = Company(name='Microsoft Corporation', short_name='Microsoft', country_code='US', sector_id=1, isin='US5949181045')
    db_session.add_all([first, second])
    db_session.flush()
    db_session.add_all([
        CompanySymbol(company_id=first.id, exchange_id=1, provider='test', symbol='AAPL', is_primary=True),
        CompanySymbol(company_id=second.id, exchange_id=1, provider='test', symbol='MSFT', is_primary=True),
    ])
    db_session.commit()
    return first, second


def test_company_search_matches_company_name(db_session):
    seed_company_search_data(db_session)
    result = companies(q='Apple', country=None, sector_id=None, exchange=None, limit=50, offset=0, db=db_session)
    assert [item.name for item in result] == ['Apple Inc.']


def test_company_search_matches_symbol_and_applies_filters(db_session):
    seed_company_search_data(db_session)
    result = companies(q='MSFT', country='US', sector_id=1, exchange='NASDAQ', limit=50, offset=0, db=db_session)
    assert [item.name for item in result] == ['Microsoft Corporation']


def test_company_search_returns_empty_for_unknown_exchange(db_session):
    seed_company_search_data(db_session)
    result = companies(q=None, country=None, sector_id=None, exchange='UNKNOWN', limit=50, offset=0, db=db_session)
    assert result == []
