import httpx
from bs4 import BeautifulSoup
from decimal import Decimal
from typing import Tuple, List, Dict
from urllib.parse import urlparse
from ..schemas.product import ProductIn, OfferIn

class KaspiParserService:
    async def fetch_and_parse(self, url: str) -> Tuple[ProductIn, List[OfferIn]]:
        async with httpx.AsyncClient(timeout=30.0, headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            html = resp.text

        soup = BeautifulSoup(html, "lxml")

        name = self._extract_name(soup)
        category = self._extract_category(soup)
        min_price, max_price = self._extract_prices(soup)
        rating = self._extract_rating(soup)
        reviews_count = self._extract_reviews_count(soup)
        offers = self._extract_offers(soup)
        attributes = self._extract_attributes(soup)
        images = self._extract_images(soup)
        sellers_count = self._extract_sellers_count(soup, offers)

        product_id = self._parse_product_id_from_url(url)

        product = ProductIn(
            name=name or "",
            category=category,
            min_price=min_price,
            max_price=max_price,
            rating=rating,
            reviews_count=reviews_count,
            offers=offers,
            attributes=attributes or None,
            images=images,
            sellers_count=sellers_count,
            source_url=url,
            source_product_id=product_id,
        )
        return product, offers

    def _extract_name(self, soup: BeautifulSoup) -> str | None:
        title = soup.find("h1")
        return title.get_text(strip=True) if title else None

    def _extract_category(self, soup: BeautifulSoup) -> str | None:
        breadcrumb = soup.select_one("nav a[href*='catalog']")
        if breadcrumb:
            return breadcrumb.get_text(strip=True)
        return None

    def _extract_prices(self, soup: BeautifulSoup) -> tuple[Decimal | None, Decimal | None]:
        price_texts = [e.get_text(strip=True) for e in soup.select("[class*='price']")]
        numbers: List[Decimal] = []
        for t in price_texts:
            digits = ''.join(ch for ch in t if ch.isdigit())
            if digits:
                try:
                    numbers.append(Decimal(digits))
                except Exception:
                    pass
        if not numbers:
            return None, None
        return min(numbers), max(numbers)

    def _extract_rating(self, soup: BeautifulSoup) -> float | None:
        rating_el = soup.select_one("[class*='rating']")
        if not rating_el:
            return None
        text = rating_el.get_text(strip=True).replace(',', '.')
        try:
            num = ''
            for ch in text:
                if ch.isdigit() or ch in ".,":
                    num += ch
                elif num:
                    break
            return float(num)
        except Exception:
            return None

    def _extract_reviews_count(self, soup: BeautifulSoup) -> int | None:
        rev = soup.find(string=lambda s: isinstance(s, str) and "отзыв" in s.lower())
        if not rev:
            return None
        digits = ''.join(ch for ch in rev if ch.isdigit())
        return int(digits) if digits else None

    def _extract_offers(self, soup: BeautifulSoup) -> List[OfferIn]:
        offers: List[OfferIn] = []
        rows = soup.select("[class*='merchant'], [class*='seller'], [data-merchant]")
        for row in rows:
            text = row.get_text(" ", strip=True)
            if not text:
                continue
            seller = None
            price = None
            parts = text.split()
            if parts:
                seller = parts[0]
            digits = ''.join(ch for ch in text if ch.isdigit())
            if digits:
                try:
                    price = Decimal(digits)
                except Exception:
                    price = None
            if seller and price is not None:
                offers.append(OfferIn(seller=seller, price=price))
        return offers

    def _extract_attributes(self, soup: BeautifulSoup) -> Dict[str, str]:
        attrs: Dict[str, str] = {}
        rows = soup.select("[class*='specs'], [class*='characteristic'], table tr")
        for r in rows:
            cells = r.find_all(["td", "th", "div", "span"], recursive=True)
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True)
                val = cells[1].get_text(strip=True)
                if key and val:
                    attrs[key] = val
        return attrs

    def _extract_images(self, soup: BeautifulSoup) -> List[str]:
        urls: List[str] = []
        for img in soup.select("img"):
            src = img.get("src") or img.get("data-src")
            if src and src.startswith("http"):
                urls.append(src)
        # unique preserve order
        seen = set()
        unique = []
        for u in urls:
            if u not in seen:
                seen.add(u)
                unique.append(u)
        return unique

    def _extract_sellers_count(self, soup: BeautifulSoup, offers: List[OfferIn]) -> int | None:
        if offers:
            return len(offers)
        txt = soup.find(string=lambda s: isinstance(s, str) and "продавц" in s.lower())
        if txt:
            digits = ''.join(ch for ch in txt if ch.isdigit())
            return int(digits) if digits else None
        return None

    def _parse_product_id_from_url(self, url: str) -> str | None:
        # URL example: .../p/<slug>-<id>/
        try:
            path = urlparse(url).path.strip("/")
            parts = path.split("/")
            for p in parts:
                if p.isdigit():
                    return p
                if "-" in p:
                    last = p.split("-")[-1]
                    if last.isdigit():
                        return last
        except Exception:
            return None
        return None
