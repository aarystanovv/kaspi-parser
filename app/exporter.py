from pathlib import Path
import orjson
from typing import Iterable
from .db.models import Product, Offer

class Exporter:
    def __init__(self, export_dir: str):
        self.base = Path(export_dir)
        self.base.mkdir(parents=True, exist_ok=True)

    def export_product(self, product: Product) -> None:
        data = {
            "id": product.id,
            "name": product.name,
            "category": product.category,
            "min_price": str(product.min_price) if product.min_price is not None else None,
            "max_price": str(product.max_price) if product.max_price is not None else None,
            "rating": product.rating,
            "reviews_count": product.reviews_count,
            "attributes": product.attributes or {},
            "images": product.images or [],
            "sellers_count": product.sellers_count,
        }
        (self.base / "product.json").write_bytes(orjson.dumps(data, option=orjson.OPT_INDENT_2))

    def export_offers(self, offers: Iterable, product_id: int) -> None:
        path = self.base / "offers.jsonl"
        with path.open("wb") as f:
            for o in offers:
                row = {"product_id": product_id, "seller": getattr(o, 'seller', None), "price": str(getattr(o, 'price', None))}
                f.write(orjson.dumps(row) + b"\n")
