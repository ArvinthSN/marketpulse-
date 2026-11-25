from app.registry.synchronizer import sync_registry
from app.ingestion.discovery.discovery_service import DiscoveryService


def test_csv_discovery_validation_and_deduplication(db_session, tmp_path):
    sync_registry(db_session)
    path = tmp_path / 'universe.csv'
    path.write_text(
        'country_code,exchange_code,symbol,company_name,currency,instrument_type,active\n'
        'IN,NSE,RELIANCE.NS,Reliance Industries,INR,equity,true\n'
        'IN,NSE,RELIANCE.NS,Reliance Industries,INR,equity,true\n'
        'US,NSE,INVALID,Invalid Ownership,USD,equity,true\n',
        encoding='utf-8',
    )
    report = DiscoveryService(db_session).import_instruments(str(path), 'IN', 'NSE')
    assert report.total_discovered == 3
    assert report.validated == 1
    assert report.duplicates == 1
    assert report.rejected == 1
