from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from ..db.models import Product, Offer
from ..schemas.product import ProductIn, OfferIn
from typing import List

class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert_product_with_offers(self, product_in: ProductIn, offers_in: List[OfferIn]) -> Product:
        if product_in.source_product_id:
            query = select(Product).where(Product.source_product_id == product_in.source_product_id)
        else:
            query = select(Product).where(Product.name == product_in.name)

        existing = self.db.execute(query).scalar_one_or_none()

        if existing is None:
            existing = Product(
                name=product_in.name,
                category=product_in.category,
                min_price=product_in.min_price,
                max_price=product_in.max_price,
                rating=product_in.rating,
                reviews_count=product_in.reviews_count,
                attributes=product_in.attributes,
                images=product_in.images,
                sellers_count=product_in.sellers_count,
                source_url=product_in.source_url,
                source_product_id=product_in.source_product_id,
            )
            self.db.add(existing)
            self.db.flush()
        else:
            existing.category = product_in.category
            existing.min_price = product_in.min_price
            existing.max_price = product_in.max_price
            existing.rating = product_in.rating
            existing.reviews_count = product_in.reviews_count
            existing.attributes = product_in.attributes
            existing.images = product_in.images
            existing.sellers_count = product_in.sellers_count
            existing.source_url = product_in.source_url

        self.db.execute(delete(Offer).where(Offer.product_id == existing.id))
        for o in offers_in:
            self.db.add(Offer(product_id=existing.id, seller=o.seller, price=o.price))

        self.db.commit()
        self.db.refresh(existing)
        return existing
