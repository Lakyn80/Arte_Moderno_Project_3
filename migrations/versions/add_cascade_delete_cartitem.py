"""Přidání kaskádového mazání do CartItem"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'new_migration_id'  # (nech tak, nebo změň dle konkrétního názvu souboru, pokud je jiný)
down_revision = 'f26fccac8667'  # předchozí platná migrace
branch_labels = None
depends_on = None


def upgrade():
    # Přidání cizího klíče s ON DELETE CASCADE
    with op.batch_alter_table('cart_item', schema=None) as batch_op:
        batch_op.create_foreign_key(
            'cart_item_product_id_fkey',  # název constraintu
            'product',                    # cílová tabulka
            ['product_id'],               # sloupec ve zdrojové tabulce
            ['id'],                       # sloupec v cílové tabulce
            ondelete='CASCADE'
        )


def downgrade():
    # Odebrání cizího klíče při rollbacku
    with op.batch_alter_table('cart_item', schema=None) as batch_op:
        batch_op.drop_constraint('cart_item_product_id_fkey', type_='foreignkey')
