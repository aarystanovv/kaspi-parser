from fastapi import APIRouter, Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..services.parser import KaspiParserService
from ..repositories.product_repository import ProductRepository
from ..exporter import Exporter
from ..core.config import settings
import json

router = APIRouter()

@router.post("/parse")
async def parse_from_seed(db: Session = Depends(get_db)):
    try:
        with open("seed.json", "r", encoding="utf-8") as f:
            seed = json.load(f)
        url = seed.get("product_url")
        if not url:
            raise HTTPException(status_code=400, detail="product_url not found in seed.json")
        parser = KaspiParserService()
        product, offers = await parser.fetch_and_parse(url)
        repo = ProductRepository(db)
        db_product = repo.upsert_product_with_offers(product, offers)
        exporter = Exporter(settings.export_dir)
        exporter.export_product(db_product)
        exporter.export_offers(offers, db_product.id)
        return {"status": "ok", "product_id": db_product.id}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post("/parse/url")
async def parse_from_url(payload: dict, db: Session = Depends(get_db)):
    url = payload.get("url") or payload.get("product_url")
    if not url:
        raise HTTPException(status_code=400, detail="url is required")
    parser = KaspiParserService()
    product, offers = await parser.fetch_and_parse(url)
    repo = ProductRepository(db)
    db_product = repo.upsert_product_with_offers(product, offers)
    exporter = Exporter(settings.export_dir)
    exporter.export_product(db_product)
    exporter.export_offers(offers, db_product.id)
    return {
        "status": "ok",
        "product_id": db_product.id,
        "name": product.name,
        "category": product.category,
        "min_price": str(product.min_price) if product.min_price is not None else None,
        "max_price": str(product.max_price) if product.max_price is not None else None,
        "rating": product.rating,
        "reviews_count": product.reviews_count,
        "sellers_count": product.sellers_count,
        "offers_count": len(offers),
        "images_count": len(product.images),
        "source_url": product.source_url,
        "source_product_id": product.source_product_id,
    }
