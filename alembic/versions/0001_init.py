from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('min_price', sa.Numeric(12, 2), nullable=True),
        sa.Column('max_price', sa.Numeric(12, 2), nullable=True),
        sa.Column('rating', sa.Float(), nullable=True),
        sa.Column('reviews_count', sa.Integer(), nullable=True),
        sa.Column('attributes', sa.JSON(), nullable=True),
        sa.Column('images', sa.JSON(), nullable=True),
        sa.Column('sellers_count', sa.Integer(), nullable=True),
    )

    op.create_table(
        'offers',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('seller', sa.String(), nullable=False),
        sa.Column('price', sa.Numeric(12, 2), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('offers')
    op.drop_table('products')
