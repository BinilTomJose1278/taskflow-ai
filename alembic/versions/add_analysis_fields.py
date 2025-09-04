"""Add analysis fields to documents table

Revision ID: add_analysis_fields
Revises: 
Create Date: 2024-01-04 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_analysis_fields'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add analysis fields to documents table
    op.add_column('documents', sa.Column('analysis_status', sa.String(50), default='pending'))
    op.add_column('documents', sa.Column('analysis_results', sa.Text))
    op.add_column('documents', sa.Column('analysis_started_at', sa.DateTime))
    op.add_column('documents', sa.Column('analysis_completed_at', sa.DateTime))
    op.add_column('documents', sa.Column('analysis_error', sa.Text))


def downgrade():
    # Remove analysis fields from documents table
    op.drop_column('documents', 'analysis_error')
    op.drop_column('documents', 'analysis_completed_at')
    op.drop_column('documents', 'analysis_started_at')
    op.drop_column('documents', 'analysis_results')
    op.drop_column('documents', 'analysis_status')
