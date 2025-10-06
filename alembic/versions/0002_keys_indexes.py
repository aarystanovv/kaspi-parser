from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0002_keys_indexes'
down_revision = '0001_init'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # add new columns to products
    op.add_column('products', sa.Column('source_url', sa.String(), nullable=True))
    op.add_column('products', sa.Column('source_product_id', sa.String(), nullable=True))
    op.add_column('products', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('products', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))

    # indexes and constraints
    op.create_unique_constraint('uq_products_source_product_id', 'products', ['source_product_id'])
    op.create_index('ix_products_category', 'products', ['category'])
    op.create_index('ix_products_min_price', 'products', ['min_price'])
    op.create_index('ix_products_rating', 'products', ['rating'])
    op.create_index('ix_products_sellers_count', 'products', ['sellers_count'])
    op.create_index('ix_products_source_url', 'products', ['source_url'])
    op.create_index('ix_products_source_product_id', 'products', ['source_product_id'])

    # offers indexes
    op.create_index('ix_offers_product_id', 'offers', ['product_id'])
    op.create_index('ix_offers_seller', 'offers', ['seller'])
    op.create_index('ix_offers_price', 'offers', ['price'])


def downgrade() -> None:
    # drop offers indexes
    op.drop_index('ix_offers_price', table_name='offers')
    op.drop_index('ix_offers_seller', table_name='offers')
    op.drop_index('ix_offers_product_id', table_name='offers')

    # drop product indexes and constraints
    op.drop_index('ix_products_source_product_id', table_name='products')
    op.drop_index('ix_products_source_url', table_name='products')
    op.drop_index('ix_products_sellers_count', table_name='products')
    op.drop_index('ix_products_rating', table_name='products')
    op.drop_index('ix_products_min_price', table_name='products')
    op.drop_index('ix_products_category', table_name='products')
    op.drop_constraint('uq_products_source_product_id', 'products', type_='unique')

    # drop columns
    op.drop_column('products', 'updated_at')
    op.drop_column('products', 'created_at')
    op.drop_column('products', 'source_product_id')
    op.drop_column('products', 'source_url')
