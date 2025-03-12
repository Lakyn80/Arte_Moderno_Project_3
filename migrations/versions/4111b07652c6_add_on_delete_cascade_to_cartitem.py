"""Add ON DELETE CASCADE to CartItem

Revision ID: 4111b07652c6
Revises: 7b9b025b545a
Create Date: 2025-03-12 14:24:27.518036
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '4111b07652c6'
down_revision = '7b9b025b545a'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('cart_item', schema=None) as batch_op:
        batch_op.drop_constraint('cart_item_product_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'cart_item_product_id_fkey',
            'product',
            ['product_id'],
            ['id'],
            ondelete='CASCADE'
        )

def downgrade():
    with op.batch_alter_table('cart_item', schema=None) as batch_op:
        batch_op.drop_constraint('cart_item_product_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'cart_item_product_id_fkey',
            'product',
            ['product_id'],
            ['id']
        )
