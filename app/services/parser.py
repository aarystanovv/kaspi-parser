import httpx
from bs4 import BeautifulSoup
from decimal import Decimal
from typing import Tuple, List, Dict
from urllib.parse import urlparse
from ..schemas.product import ProductIn, OfferIn
import json
from typing import Any

class KaspiParserService:
    async def fetch_and_parse(self, url: str) -> Tuple[ProductIn, List[OfferIn]]:
        async with httpx.AsyncClient(timeout=30.0, headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            html = resp.text

        soup = BeautifulSoup(html, "lxml")

        ld = self._extract_ld_json(soup)
        name = self._extract_name(soup, ld)
        category = self._extract_category(soup, ld)
        offers = self._extract_offers(soup, ld)
        min_price, max_price = self._extract_prices(soup, ld, offers)
        rating = self._extract_rating(soup, ld)
        reviews_count = self._extract_reviews_count(soup, ld)
        attributes = self._extract_attributes(soup)
        images = self._extract_images(soup, ld)
        sellers_count = self._extract_sellers_count(soup, ld, offers)

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

    def _extract_ld_json(self, soup: BeautifulSoup) -> dict[str, Any] | None:
        for s in soup.select("script[type='application/ld+json']"):
            try:
                raw = s.string or ""
                if not raw.strip():
                    continue
                data = json.loads(raw)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get("@type") == "Product":
                            return item
                if isinstance(data, dict) and data.get("@type") == "Product":
                    return data
            except Exception:
                continue
        return None

    def _extract_name(self, soup: BeautifulSoup, ld: dict[str, Any] | None) -> str | None:
        if ld and isinstance(ld.get("name"), str):
            return ld["name"].strip()
        title = soup.find("h1")
        return title.get_text(strip=True) if title else None

    def _extract_category(self, soup: BeautifulSoup, ld: dict[str, Any] | None) -> str | None:
        if ld:
            val = ld.get("category") or ld.get("breadcrumb")
            if isinstance(val, str) and val.strip():
                return val.strip()
        breadcrumb = soup.select_one("[data-testid='breadcrumb'] a, nav[aria-label*='хлеб'] a, nav a[href*='catalog']")
        if breadcrumb:
            return breadcrumb.get_text(strip=True)
        return None

    def _extract_prices(self, soup: BeautifulSoup, ld: dict[str, Any] | None, offers: List[OfferIn]) -> tuple[Decimal | None, Decimal | None]:
        numbers: List[Decimal] = []
        if offers:
            for o in offers:
                try:
                    numbers.append(Decimal(o.price))
                except Exception:
                    pass
        if ld:
            offers = ld.get("offers")
            if isinstance(offers, dict):
                for key in ("price", "lowPrice", "highPrice"):
                    val = offers.get(key)
                    if val is not None:
                        try:
                            numbers.append(Decimal(str(val).replace(',', '.')))
                        except Exception:
                            pass
            elif isinstance(offers, list): 
                for o in offers:
                    if not isinstance(o, dict):
                        continue
                    price_val = o.get("price")
                    if price_val is not None:
                        try:
                            numbers.append(Decimal(str(price_val).replace(',', '.')))
                        except Exception:
                            pass
        price_texts = [e.get_text(strip=True) for e in soup.select("[data-testid*='price'], .item__price-once, [class*='price']")]
        for t in price_texts:
            digits = ''.join(ch for ch in t if ch.isdigit())
            if digits:
                try:
                    numbers.append(Decimal(digits))
                except Exception:
                    pass
        for cell in soup.select(".sellers-table__price-cell-text:not(._installments-price)"):
            txt = cell.get_text(strip=True)
            digits = ''.join(ch for ch in txt if ch.isdigit())
            if digits:
                try:
                    numbers.append(Decimal(digits))
                except Exception:
                    pass
        if not numbers:
            return None, None
        return min(numbers), max(numbers)

    def _extract_rating(self, soup: BeautifulSoup, ld: dict[str, Any] | None) -> float | None:
        if ld and isinstance(ld.get("aggregateRating"), dict):
            val = ld["aggregateRating"].get("ratingValue")
            if val is not None:
                try:
                    return float(str(val).replace(',', '.'))
                except Exception:
                    pass
        micro = soup.select_one("[itemprop='ratingValue']")
        if micro and micro.get("content"):
            try:
                return float(str(micro.get("content")).replace(',', '.'))
            except Exception:
                pass
        best: float | None = None
        for el in soup.select(".rating"):
            classes = el.get("class", [])
            if any("_seller" in c for c in classes):
                continue
            for c in classes:
                if len(c) == 3 and c.startswith("_") and c[1:].isdigit():
                    try:
                        val = int(c[1:]) / 10.0
                        if best is None or val > best:
                            best = val
                    except Exception:
                        continue
        if best is not None:
            return best
        rating_el = soup.select_one("[data-testid*='rating'], [class*='rating']")
        if rating_el:
            text = rating_el.get_text(strip=True).replace(',', '.')
            try:
                num = ''
                for ch in text:
                    if ch.isdigit() or ch in ".,":
                        num += ch
                    elif num:
                        break
                return float(num) if num else None
            except Exception:
                return None
        return None

    def _extract_reviews_count(self, soup: BeautifulSoup, ld: dict[str, Any] | None) -> int | None:
        if ld and isinstance(ld.get("aggregateRating"), dict):
            val = ld["aggregateRating"].get("reviewCount")
            if val is not None:
                try:
                    c = int(str(val))
                    return c if 0 <= c <= 1_000_000 else None
                except Exception:
                    pass
        micro = soup.select_one("[itemprop='reviewCount']")
        if micro and micro.get("content"):
            try:
                c = int(str(micro.get("content")))
                return c if 0 <= c <= 1_000_000 else None
            except Exception:
                pass
        best = 0
        for el in soup.select(".rating-count, [class*='rating-count']"):
            txt = el.get_text(strip=True)
            digits = ''.join(ch for ch in txt if ch.isdigit())
            if digits and 1 <= len(digits) <= 6:
                try:
                    val = int(digits)
                    if 0 <= val <= 1_000_000 and val > best:
                        best = val
                except Exception:
                    continue
        if best:
            return best
        texts = soup.find_all(string=lambda s: isinstance(s, str) and any(k in s.lower() for k in ["отзыв", "пікір", "review"]))
        for t in texts:
            digits = ''.join(ch for ch in t if ch.isdigit())
            if digits and 1 <= len(digits) <= 6:
                try:
                    val = int(digits)
                    if 0 <= val <= 1_000_000 and val > best:
                        best = val
                except Exception:
                    continue
        return best or None

    def _extract_offers(self, soup: BeautifulSoup, ld: dict[str, Any] | None) -> List[OfferIn]:
        offers: List[OfferIn] = []
        if ld:
            ld_offers = ld.get("offers")
            if isinstance(ld_offers, list):
                for o in ld_offers:
                    if not isinstance(o, dict):
                        continue
                    seller_name = None
                    seller = o.get("seller")
                    if isinstance(seller, dict):
                        seller_name = seller.get("name")
                    elif isinstance(seller, str):
                        seller_name = seller
                    price_val = o.get("price")
                    if seller_name and price_val is not None:
                        try:
                            price = Decimal(str(price_val).replace(',', '.'))
                            offers.append(OfferIn(seller=seller_name, price=price))
                        except Exception:
                            pass
        if not offers:
            for tr in soup.select("tbody tr"):
                first_td = tr.find("td")
                seller_name = None
                if first_td:
                    a = first_td.find("a")
                    if a and a.get_text(strip=True):
                        seller_name = a.get_text(strip=True)
                price_div = tr.select_one(".sellers-table__price-cell-text:not(._installments-price), .sellers-table__price-cell-text")
                price_val: Decimal | None = None
                if price_div:
                    txt = price_div.get_text(strip=True)
                    digits = ''.join(ch for ch in txt if ch.isdigit())
                    if digits:
                        try:
                            price_val = Decimal(digits)
                        except Exception:
                            price_val = None
                if seller_name and price_val is not None:
                    offers.append(OfferIn(seller=seller_name, price=price_val))
        return offers

    def _extract_sellers_count(self, soup: BeautifulSoup, ld: dict[str, Any] | None, offers: List[OfferIn]) -> int | None:
        if offers:
            return len(offers)
        if ld and isinstance(ld.get("offers"), dict): 
            offer_count = ld["offers"].get("offerCount")
            if offer_count is not None:
                try:
                    return int(str(offer_count))
                except Exception:
                    pass
        txt = soup.find(string=lambda s: isinstance(s, str) and "продавц" in s.lower())
        if txt:
            digits = ''.join(ch for ch in txt if ch.isdigit())
            return int(digits) if digits else None
        return None

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

    def _extract_images(self, soup: BeautifulSoup, ld: dict[str, Any] | None) -> List[str]:
        urls: List[str] = []
        if ld:
            img = ld.get("image")
            if isinstance(img, list):
                for it in img:
                    if isinstance(it, str) and it.startswith("http"):
                        urls.append(it)
                    elif isinstance(it, dict):
                        u = it.get("url") or it.get("contentUrl")
                        if isinstance(u, str) and u.startswith("http"):
                            urls.append(u)
            elif isinstance(img, dict):
                u = img.get("url") or img.get("contentUrl")
                if isinstance(u, str) and u.startswith("http"):
                    urls.append(u)
            elif isinstance(img, str) and img.startswith("http"):
                urls.append(img)
            video = ld.get("video")
            if isinstance(video, list):
                for v in video:
                    if isinstance(v, dict):
                        u = v.get("contentUrl") or v.get("embedUrl") or v.get("url")
                        if isinstance(u, str) and u.startswith("http"):
                            urls.append(u)
            elif isinstance(video, dict):
                u = video.get("contentUrl") or video.get("embedUrl") or video.get("url")
                if isinstance(u, str) and u.startswith("http"):
                    urls.append(u)

        for img_tag in soup.select("img, source"): 
            candidates = [
                img_tag.get("src"),
                img_tag.get("data-src"),
                img_tag.get("data-original"),
                img_tag.get("data-lazy"),
            ]
            srcset = img_tag.get("srcset") or img_tag.get("data-srcset")
            if srcset:
                for part in srcset.split(","):
                    u = part.strip().split(" ")[0]
                    if u:
                        candidates.append(u)
            for c in candidates:
                if isinstance(c, str) and c.startswith("http"):
                    urls.append(c)

        for el in soup.select("[data-image], [data-image-url], [data-video], [data-video-url]"):
            for attr in ("data-image", "data-image-url", "data-video", "data-video-url"):
                val = el.get(attr)
                if isinstance(val, str) and val.startswith("http"):
                    urls.append(val)

        seen = set()
        unique = []
        for u in urls:
            if u not in seen:
                seen.add(u)
                unique.append(u)
        return unique

    def _parse_product_id_from_url(self, url: str) -> str | None:
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
