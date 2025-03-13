"""Add order_number to Order table"""

from alembic import op
import sqlalchemy as sa

# Revize
revision = '20250314_add_order_number'
down_revision = 'fbfbf930fa6f'  # ← změň na správný kód podle předchozí revize
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('order', sa.Column('order_number', sa.String(length=32), nullable=True))
    op.create_unique_constraint("uq_order_order_number", "order", ["order_number"])

def downgrade():
    op.drop_constraint("uq_order_order_number", "order", type_='unique')
    op.drop_column('order', 'order_number')
