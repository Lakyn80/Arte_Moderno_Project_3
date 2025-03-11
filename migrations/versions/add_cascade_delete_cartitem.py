"""Přidání kaskádového mazání do CartItem"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'new_migration_id'  # Vygeneruješ příkazem `flask db migrate -m "Přidání kaskádového mazání"`
down_revision = 'f26fccac8667'

branch_labels = None
depends_on = None


def upgrade():
    # Nejprve odstraníme starý cizí klíč (musíme znát jeho jméno)
    with op.batch_alter_table('cart_item', schema=None) as batch_op:
        batch_op.drop_constraint('cart_item_product_id_fkey', type_='foreignkey')  # ✅ Uprav název podle DB

    # Pak přidáme nový cizí klíč s `ON DELETE CASCADE`
    with op.batch_alter_table('cart_item', schema=None) as batch_op:
        batch_op.create_foreign_key('cart_item_product_id_fkey', 'product', ['product_id'], ['id'], ondelete='CASCADE')


def downgrade():
    # Při rollbacku odstraníme nově přidaný constraint
    with op.batch_alter_table('cart_item', schema=None) as batch_op:
        batch_op.drop_constraint('cart_item_product_id_fkey', type_='foreignkey')

    # A vrátíme zpět původní cizí klíč bez CASCADE
    with op.batch_alter_table('cart_item', schema=None) as batch_op:
        batch_op.create_foreign_key('cart_item_product_id_fkey', 'product', ['product_id'], ['id'])
