"""initial schema

Revision ID: 001_initial
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('countries', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('code', sa.String(2), nullable=False), sa.Column('name', sa.String(100), nullable=False), sa.Column('currency', sa.String(3), nullable=False), sa.Column('timezone', sa.String(50), nullable=False), sa.UniqueConstraint('code'))
    op.create_index('ix_countries_code', 'countries', ['code'], unique=True)
    op.create_table('sectors', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('name', sa.String(100), nullable=False), sa.UniqueConstraint('name'))
    op.create_table('exchanges', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('code', sa.String(20), nullable=False), sa.Column('name', sa.String(150), nullable=False), sa.Column('country_code', sa.String(2), sa.ForeignKey('countries.code', onupdate='CASCADE'), nullable=False), sa.Column('yahoo_suffix', sa.String(20)), sa.Column('currency', sa.String(3), nullable=False), sa.Column('timezone', sa.String(50), nullable=False), sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.true()), sa.UniqueConstraint('code'))
    op.create_index('ix_exchanges_code', 'exchanges', ['code'], unique=True)
    op.create_index('ix_exchanges_country_code', 'exchanges', ['country_code'])
    op.create_table('companies', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('country_code', sa.String(2), sa.ForeignKey('countries.code'), nullable=True), sa.Column('sector_id', sa.Integer(), sa.ForeignKey('sectors.id'), nullable=True), sa.Column('name', sa.String(300), nullable=False), sa.Column('short_name', sa.String(300)), sa.Column('website', sa.String(500)), sa.Column('market_cap', sa.Numeric(20, 2)), sa.Column('isin', sa.String(20)), sa.Column('created_at', sa.DateTime(), nullable=False), sa.Column('updated_at', sa.DateTime(), nullable=False), sa.UniqueConstraint('isin', name='uq_companies_isin'))
    op.create_index('ix_companies_country_code', 'companies', ['country_code'])
    op.create_index('ix_companies_sector_id', 'companies', ['sector_id'])
    op.create_table('company_symbols', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('company_id', sa.Integer(), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False), sa.Column('exchange_id', sa.Integer(), sa.ForeignKey('exchanges.id', ondelete='CASCADE'), nullable=False), sa.Column('provider', sa.String(50), nullable=False), sa.Column('symbol', sa.String(50), nullable=False), sa.Column('is_primary', sa.Boolean(), nullable=False, server_default=sa.false()), sa.UniqueConstraint('provider', 'exchange_id', 'symbol', name='uq_provider_exchange_symbol'))
    op.create_index('ix_company_symbols_company_id', 'company_symbols', ['company_id'])
    op.create_index('ix_company_symbols_exchange_id', 'company_symbols', ['exchange_id'])
    op.create_table('historical_prices', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('company_symbol_id', sa.Integer(), sa.ForeignKey('company_symbols.id', ondelete='CASCADE'), nullable=False), sa.Column('timestamp', sa.DateTime(), nullable=False), sa.Column('open', sa.Numeric(18, 6), nullable=False), sa.Column('high', sa.Numeric(18, 6), nullable=False), sa.Column('low', sa.Numeric(18, 6), nullable=False), sa.Column('close', sa.Numeric(18, 6), nullable=False), sa.Column('volume', sa.Integer(), nullable=False), sa.Column('currency', sa.String(3), nullable=False), sa.Column('interval', sa.String(20), nullable=False), sa.Column('source', sa.String(50), nullable=False), sa.UniqueConstraint('company_symbol_id', 'timestamp', 'interval', name='uq_symbol_timestamp_interval'))
    op.create_index('ix_history_symbol_timestamp', 'historical_prices', ['company_symbol_id', 'timestamp'])
    op.create_table('ingestion_runs', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('scope_type', sa.String(20), nullable=False), sa.Column('scope_value', sa.String(20)), sa.Column('status', sa.String(20), nullable=False, server_default='running'), sa.Column('period', sa.String(20)), sa.Column('interval', sa.String(20)), sa.Column('successful', sa.Integer(), nullable=False, server_default='0'), sa.Column('failed', sa.Integer(), nullable=False, server_default='0'), sa.Column('inserted', sa.Integer(), nullable=False, server_default='0'), sa.Column('updated', sa.Integer(), nullable=False, server_default='0'), sa.Column('rejected', sa.Integer(), nullable=False, server_default='0'), sa.Column('started_at', sa.DateTime(), nullable=False), sa.Column('finished_at', sa.DateTime()), sa.Column('error_summary', sa.Text()))
    op.create_index('ix_ingestion_runs_status', 'ingestion_runs', ['status'])
    op.create_table('market_snapshots', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('exchange_id', sa.Integer(), sa.ForeignKey('exchanges.id', ondelete='CASCADE'), nullable=False), sa.Column('timestamp', sa.DateTime(), nullable=False), sa.Column('metadata_json', sa.Text()))
    op.create_index('ix_market_snapshots_exchange_id', 'market_snapshots', ['exchange_id'])
    op.create_table('data_quality_events', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('run_id', sa.Integer(), sa.ForeignKey('ingestion_runs.id', ondelete='SET NULL'), nullable=True), sa.Column('company_symbol_id', sa.Integer(), sa.ForeignKey('company_symbols.id', ondelete='SET NULL'), nullable=True), sa.Column('event_type', sa.String(50), nullable=False), sa.Column('severity', sa.String(20), nullable=False), sa.Column('message', sa.Text(), nullable=False), sa.Column('payload', sa.Text()), sa.Column('created_at', sa.DateTime(), nullable=False))
    op.create_index('ix_data_quality_events_run_id', 'data_quality_events', ['run_id'])


def downgrade() -> None:
    for table in ('data_quality_events', 'market_snapshots', 'ingestion_runs', 'historical_prices', 'company_symbols', 'companies', 'exchanges', 'sectors', 'countries'):
        op.drop_table(table)
