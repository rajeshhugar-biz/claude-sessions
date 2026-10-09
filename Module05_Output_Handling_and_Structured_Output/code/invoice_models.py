"""Pydantic models for the lab invoice. All data in this pack is fictional."""
from datetime import date
from typing import Literal, Optional
from pydantic import BaseModel, Field


class LineItem(BaseModel):
    description: str
    quantity: int = Field(ge=1)
    unit_price: float = Field(ge=0)
    amount: float = Field(ge=0, description="Line total exactly as printed")


class Invoice(BaseModel):
    invoice_number: str
    invoice_date: date  # ISO 8601, e.g. 2026-09-30
    due_date: Optional[date]  # required key; null if not printed
    vendor_name: str
    customer_name: str
    currency: Literal["INR", "USD", "EUR"]
    line_items: list[LineItem] = Field(min_length=1)
    subtotal: float
    tax_rate_percent: Optional[float]
    tax_amount: float
    total: float
    notes: Optional[str] = None  # optional: the key may be left out
