from __future__ import annotations

from fastapi import FastAPI, Response

from .models import Quote
from .pdf import generate_pdf_bytes

app = FastAPI(title="Devis PDF")


@app.post("/quote")
def create_quote_pdf(quote: Quote) -> Response:
    pdf_bytes = generate_pdf_bytes(quote)
    return Response(content=pdf_bytes, media_type="application/pdf")
