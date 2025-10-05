import asyncio
import json
from sqlalchemy import text
from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.core.config import settings
from app.logging_config import setup_logging, get_logger
from app.scheduler import start_scheduler
from app.services.parser import KaspiParserService
from app.repositories.product_repository import ProductRepository
from app.exporter import Exporter


async def run_once() -> None:
    with open("seed.json", "r", encoding="utf-8") as f:
        seed = json.load(f)
    url = seed.get("product_url")
    if not url:
        raise RuntimeError("product_url not found in seed.json")

    parser = KaspiParserService()
    product, offers = await parser.fetch_and_parse(url)

    db = SessionLocal()
    try:
        repo = ProductRepository(db)
        db_product = repo.upsert_product_with_offers(product, offers)
        exporter = Exporter(settings.export_dir)
        exporter.export_product(db_product)
        exporter.export_offers(offers, db_product.id)
    finally:
        db.close()


def main() -> None:
    setup_logging()
    logger = get_logger()
    logger.info("init", event="startup", env=settings.app_env)

    # create tables
    Base.metadata.create_all(bind=engine)

    # optional scheduler
    start_scheduler()

    # run one parse
    asyncio.run(run_once())


if __name__ == "__main__":
    main()
