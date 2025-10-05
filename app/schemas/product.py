from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from decimal import Decimal
from datetime import datetime

class OfferIn(BaseModel):
    seller: str
    price: Decimal

class OfferOut(OfferIn):
    id: int
    product_id: int

    class Config:
        from_attributes = True

class ProductIn(BaseModel):
    name: str
    category: Optional[str] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    rating: Optional[float] = Field(default=None, ge=0, le=5)
    reviews_count: Optional[int] = Field(default=None, ge=0)
    offers: List[OfferIn] = Field(default_factory=list)
    attributes: Optional[Dict[str, str]] = None
    images: List[str] = Field(default_factory=list)
    sellers_count: Optional[int] = Field(default=None, ge=0)

    source_url: Optional[str] = None
    source_product_id: Optional[str] = None

class ProductOut(BaseModel):
    id: int
    name: str
    category: Optional[str]
    min_price: Optional[Decimal]
    max_price: Optional[Decimal]
    rating: Optional[float]
    reviews_count: Optional[int]
    attributes: Optional[Dict[str, str]]
    images: List[str]
    sellers_count: Optional[int]
    source_url: Optional[str]
    source_product_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
