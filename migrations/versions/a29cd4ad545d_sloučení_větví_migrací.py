"""Sloučení větví migrací

Revision ID: a29cd4ad545d
Revises: 7b9b025b545a, new_migration_id
Create Date: 2025-03-12 01:05:16.563895

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a29cd4ad545d'
down_revision = ('7b9b025b545a', 'new_migration_id')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
