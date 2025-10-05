from sqlalchemy import Column, Integer, String, Float, ForeignKey, Numeric, DateTime, func, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .base import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    min_price = Column(Numeric(12, 2), nullable=True, index=True)
    max_price = Column(Numeric(12, 2), nullable=True)
    rating = Column(Float, nullable=True, index=True)
    reviews_count = Column(Integer, nullable=True)

    # source identifiers
    source_url = Column(String, nullable=True, index=True)
    source_product_id = Column(String, nullable=True, index=True)

    # extended fields
    attributes = Column(JSONB, nullable=True)  # key-value pairs
    images = Column(JSONB, nullable=True)      # list of URLs
    sellers_count = Column(Integer, nullable=True, index=True)

    # timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint('source_product_id', name='uq_products_source_product_id'),
        Index('ix_products_category', 'category'),
    )

    offers = relationship("Offer", back_populates="product", cascade="all, delete-orphan")

class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    seller = Column(String, nullable=False, index=True)
    price = Column(Numeric(12, 2), nullable=False, index=True)

    product = relationship("Product", back_populates="offers")
