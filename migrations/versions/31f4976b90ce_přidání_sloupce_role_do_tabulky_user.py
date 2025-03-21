"""Přidání sloupce role do tabulky user

Revision ID: 31f4976b90ce
Revises: 16e82a0195cc
Create Date: 2025-02-08 23:57:02.884961

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '31f4976b90ce'
down_revision = '16e82a0195cc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    def upgrade():
        with op.batch_alter_table('user', schema=None) as batch_op:
             batch_op.alter_column('role', server_default=None)


    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('role')

    # ### end Alembic commands ###
