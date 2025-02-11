"""Add last_name and address to User

Revision ID: b61a4672f274
Revises: 245ea1f5d7a0
Create Date: 2025-02-11 01:07:39.314243

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b61a4672f274'
down_revision = '245ea1f5d7a0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('last_name', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('address', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('address')
        batch_op.drop_column('last_name')

    # ### end Alembic commands ###
