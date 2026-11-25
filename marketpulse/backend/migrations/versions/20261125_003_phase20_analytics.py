"""Phase 2.0 analytics persistence.

Revision ID: 003_phase20
Revises: 002_phase11
"""
from alembic import op
import sqlalchemy as sa

revision = '003_phase20'
down_revision = '002_phase11'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('historical_prices', sa.Column('adjusted_close', sa.Numeric(18, 6)))
    op.add_column('companies', sa.Column('shares_outstanding', sa.Numeric(24, 6)))
    op.add_column('companies', sa.Column('shares_outstanding_source', sa.String(100)))
    op.add_column('companies', sa.Column('shares_outstanding_at', sa.DateTime()))

    op.create_table('exchange_rate_snapshots',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('base_currency', sa.String(3), nullable=False),
        sa.Column('quote_currency', sa.String(3), nullable=False),
        sa.Column('rate', sa.Numeric(24, 12), nullable=False),
        sa.Column('observed_at', sa.DateTime(), nullable=False),
        sa.Column('source', sa.String(100), nullable=False),
        sa.UniqueConstraint('base_currency', 'quote_currency', 'observed_at', name='uq_fx_currency_timestamp'))
    op.create_index('ix_fx_lookup', 'exchange_rate_snapshots', ['base_currency', 'quote_currency', 'observed_at'])

    op.create_table('analytics_snapshots',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('entity_type', sa.String(30), nullable=False),
        sa.Column('entity_id', sa.String(50), nullable=False),
        sa.Column('period', sa.String(20), nullable=False),
        sa.Column('reporting_currency', sa.String(3), nullable=False),
        sa.Column('methodology_version', sa.String(20), nullable=False),
        sa.Column('calculated_at', sa.DateTime(), nullable=False),
        sa.Column('source_observation_at', sa.DateTime()),
        sa.Column('coverage_json', sa.Text()),
        sa.Column('result_json', sa.Text(), nullable=False),
        sa.UniqueConstraint('entity_type', 'entity_id', 'period', 'reporting_currency', name='uq_analytics_snapshot'))
    op.create_index('ix_analytics_lookup', 'analytics_snapshots', ['entity_type', 'entity_id', 'calculated_at'])

    op.create_table('analytics_job_runs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('scope_type', sa.String(20), nullable=False),
        sa.Column('scope_value', sa.String(50)),
        sa.Column('status', sa.String(20), nullable=False, server_default='running'),
        sa.Column('periods', sa.Text(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('finished_at', sa.DateTime()),
        sa.Column('records_processed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_summary', sa.Text()))


def downgrade() -> None:
    op.drop_table('analytics_job_runs')
    op.drop_index('ix_analytics_lookup', table_name='analytics_snapshots')
    op.drop_table('analytics_snapshots')
    op.drop_index('ix_fx_lookup', table_name='exchange_rate_snapshots')
    op.drop_table('exchange_rate_snapshots')
    op.drop_column('companies', 'shares_outstanding_at')
    op.drop_column('companies', 'shares_outstanding_source')
    op.drop_column('companies', 'shares_outstanding')
    op.drop_column('historical_prices', 'adjusted_close')
