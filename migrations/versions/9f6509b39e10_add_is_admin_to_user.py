"""Add is_admin to User

Revision ID: 9f6509b39e10
Revises: 717fd37e295f
Create Date: 2025-03-13 13:29:47.635147

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f6509b39e10'
down_revision = '717fd37e295f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_column('position_id')

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_admin', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('is_admin')

    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('position_id', sa.INTEGER(), autoincrement=False, nullable=True))

    # ### end Alembic commands ###
