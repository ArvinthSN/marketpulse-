"""Phase 1.1 discovery and resumable ingestion tables.

Revision ID: 002_phase11
Revises: 001_initial
"""
from alembic import op
import sqlalchemy as sa

revision = '002_phase11'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'instrument_universes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('exchange_id', sa.Integer(), sa.ForeignKey('exchanges.id', ondelete='CASCADE'), nullable=False),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('original_symbol', sa.String(50), nullable=False),
        sa.Column('normalized_symbol', sa.String(50), nullable=False),
        sa.Column('company_name', sa.String(300), nullable=False),
        sa.Column('currency', sa.String(3)),
        sa.Column('instrument_type', sa.String(30), nullable=False, server_default='equity'),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('source', sa.String(500), nullable=False),
        sa.Column('discovered_at', sa.DateTime(), nullable=False),
        sa.Column('completeness', sa.String(30), nullable=False, server_default='partial'),
        sa.UniqueConstraint('provider', 'exchange_id', 'normalized_symbol', name='uq_universe_provider_exchange_symbol'),
    )
    op.create_index('ix_instrument_universes_exchange_id', 'instrument_universes', ['exchange_id'])

    op.create_table(
        'ingestion_items',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('run_id', sa.Integer(), sa.ForeignKey('ingestion_runs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('company_symbol_id', sa.Integer(), sa.ForeignKey('company_symbols.id', ondelete='SET NULL')),
        sa.Column('symbol', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('next_attempt_at', sa.DateTime()),
        sa.Column('last_error', sa.Text()),
        sa.Column('started_at', sa.DateTime()),
        sa.Column('finished_at', sa.DateTime()),
        sa.UniqueConstraint('run_id', 'symbol', name='uq_ingestion_run_symbol'),
    )
    op.create_index('ix_ingestion_items_run_id', 'ingestion_items', ['run_id'])
    op.create_index('ix_ingestion_items_company_symbol_id', 'ingestion_items', ['company_symbol_id'])
    op.create_index('ix_ingestion_items_status', 'ingestion_items', ['status'])


def downgrade() -> None:
    op.drop_table('ingestion_items')
    op.drop_table('instrument_universes')
