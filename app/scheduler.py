from apscheduler.schedulers.background import BackgroundScheduler
from .db.session import AsyncSessionLocal
from .services.parser import KaspiParserService
from .repositories.product_repository import ProductRepository
from .exporter import Exporter
from .core.config import settings
import json
import asyncio

scheduler = BackgroundScheduler()


def _job():
    try:
        with open("seed.json", "r", encoding="utf-8") as f:
            seed = json.load(f)
        url = seed.get("product_url")
        if not url:
            return

        async def run():
            parser = KaspiParserService()
            product, offers = await parser.fetch_and_parse(url)
            async with AsyncSessionLocal() as db:
                repo = ProductRepository(db)
                db_product = await repo.upsert_product_with_offers(product, offers)
                exporter = Exporter(settings.export_dir)
                exporter.export_product(db_product)
                exporter.export_offers(offers, db_product.id)

        asyncio.run(run())
    except Exception:
        pass


def start_scheduler():
    if settings.scheduler_enabled:
        scheduler.add_job(_job, "interval", minutes=15, id="kaspi-refresh", replace_existing=True)
        scheduler.start()
