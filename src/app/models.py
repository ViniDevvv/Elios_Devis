from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Company(BaseModel):
    name: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)
    email: str = Field(..., min_length=3)
    phone: str = Field(..., min_length=3)
    website: Optional[str] = ""
    siret: Optional[str] = ""
    vat_number: Optional[str] = ""
    iban: Optional[str] = ""
    bic: Optional[str] = ""


class Client(BaseModel):
    name: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)
    email: str = Field(..., min_length=3)
    phone: str = Field(..., min_length=3)


class QuoteItem(BaseModel):
    description: str = Field(..., min_length=1)
    quantity: float = Field(..., gt=0)
    unit_price: float = Field(..., ge=0)

    @property
    def total(self) -> float:
        return self.quantity * self.unit_price


class Quote(BaseModel):
    number: str = Field(..., min_length=1)
    issue_date: str = Field(..., min_length=1)
    due_date: str = Field(..., min_length=1)
    company: Company
    client: Client
    items: List[QuoteItem]
    tax_rate: float = Field(0.2, ge=0)
    notes: Optional[str] = ""
    status: Optional[str] = "En attente"
    payment_terms: Optional[str] = "Paiement à 30 jours."
