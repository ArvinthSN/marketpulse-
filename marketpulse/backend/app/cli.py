import argparse
from app.database.session import SessionLocal
from app.registry.synchronizer import sync_registry
from app.ingestion.providers.yahoo_provider import YahooProvider
from app.services.ingestion_service import IngestionService


def main():
    parser = argparse.ArgumentParser(prog='marketpulse')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('sync-registry')
    ingest = sub.add_parser('ingest'); ingest.add_argument('--country'); ingest.add_argument('--exchange'); ingest.add_argument('--limit',type=int,default=100); ingest.add_argument('--period',default='1y'); ingest.add_argument('--interval',default='1d')
    sub.add_parser('validate-data'); sub.add_parser('show-ingestion-status')
    discovery = sub.add_parser('import-universe')
    discovery.add_argument('--file', required=True)
    discovery.add_argument('--country')
    discovery.add_argument('--exchange')
    resume = sub.add_parser('resume-ingestion')
    resume.add_argument('--run-id', required=True, type=int)
    args = parser.parse_args()
    db = SessionLocal()
    try:
        if args.command == 'sync-registry':
            counts = sync_registry(db); print(f'Synchronized registry: {counts[0]} countries, {counts[1]} exchanges')
        elif args.command == 'ingest':
            if not args.exchange:
                print('Country ingestion is not active until a maintained exchange instrument list is configured.'); return
            run = IngestionService(db, YahooProvider()).run_exchange(args.exchange, args.limit, args.period, args.interval)
            print(f'Ingestion run {run.id}: {run.status}; inserted={run.inserted}, rejected={run.rejected}, failed={run.failed}')
        elif args.command == 'import-universe':
            from app.ingestion.discovery.discovery_service import DiscoveryService
            report = DiscoveryService(db).import_instruments(args.file, args.country, args.exchange)
            print(f'Discovery: discovered={report.total_discovered}, validated={report.validated}, rejected={report.rejected}, duplicates={report.duplicates}, completeness={report.completeness}')
        elif args.command == 'validate-data': print('No pending legacy data-validation job configured.')
        elif args.command == 'show-ingestion-status':
            from app.models.entities import IngestionRun
            for run in db.query(IngestionRun).order_by(IngestionRun.started_at.desc()).limit(20):
                print(run.id, run.status, run.scope_type, run.scope_value, run.inserted, run.failed)
        elif args.command == 'resume-ingestion':
            run = IngestionService(db, YahooProvider()).resume_run(args.run_id)
            print(f'Resumed ingestion run {run.id}: {run.status}; inserted={run.inserted}, rejected={run.rejected}, failed={run.failed}')
    finally:
        db.close()


if __name__ == '__main__': main()
