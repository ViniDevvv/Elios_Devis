from __future__ import annotations

from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.graphics.shapes import Circle, Drawing, String

from .models import Quote


def _format_currency(value: float) -> str:
    return f"{value:,.2f}".replace(",", " ")


def _build_logo() -> Drawing:
    logo = Drawing(36, 36)
    logo.add(Circle(18, 18, 18, fillColor=colors.HexColor("#111827"), strokeColor=None))
    logo.add(
        String(
            18,
            10,
            "E",
            fillColor=colors.white,
            fontSize=18,
            fontName="Helvetica-Bold",
            textAnchor="middle",
        )
    )
    return logo


def _find_logo_path() -> Path | None:
    project_root = Path(__file__).resolve().parents[2]
    asset_dir = project_root / "asset"
    if not asset_dir.exists():
        return None
    preferred = list(asset_dir.glob("Elios.*"))
    if preferred:
        return preferred[0]

    candidates = sorted(asset_dir.glob("*.png"))
    if not candidates:
        candidates = sorted(asset_dir.glob("*.jpg")) + sorted(asset_dir.glob("*.jpeg"))
    return candidates[0] if candidates else None


def generate_pdf_bytes(quote: Quote) -> bytes:
    subtotal = sum(item.total for item in quote.items)
    tax_amount = subtotal * quote.tax_rate
    total = subtotal + tax_amount

    palette = {
        "ink": colors.HexColor("#0F172A"),
        "muted": colors.HexColor("#475569"),
        "border": colors.HexColor("#E2E8F0"),
        "soft": colors.HexColor("#F8FAFC"),
        "brand": colors.HexColor("#0B5FFF"),
    }

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    brand = ParagraphStyle(
        "Brand",
        parent=styles["Title"],
        textColor=palette["ink"],
        fontSize=24,
        leading=24,
    )
    meta = ParagraphStyle(
        "Meta",
        parent=styles["BodyText"],
        textColor=palette["muted"],
        fontSize=10.5,
        leading=14,
        alignment=2,
    )
    section = ParagraphStyle(
        "Section",
        parent=styles["Heading4"],
        textColor=palette["ink"],
        spaceBefore=6,
        spaceAfter=4,
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontSize=10.7,
        leading=14,
        textColor=palette["ink"],
    )
    foot = ParagraphStyle(
        "Foot",
        parent=styles["BodyText"],
        fontSize=9,
        leading=12,
        textColor=palette["muted"],
    )

    elements = []
    logo_path = _find_logo_path()
    logo_element = _build_logo()
    if logo_path:
        logo_element = Image(str(logo_path), width=42, height=42)

    brand_block = Table(
        [[logo_element, Paragraph("Elios", brand)]],
        colWidths=[46, 180],
    )
    brand_block.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))

    meta_block = Paragraph(
        f"<b>Devis {quote.number}</b><br/>Statut: {quote.status or 'En attente'}<br/>Émis le {quote.issue_date}<br/>Échéance {quote.due_date}",
        meta,
    )

    header = Table([[brand_block, meta_block]], colWidths=[260, 200])
    header.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LINEBELOW", (0, 0), (-1, 0), 0.6, palette["border"]),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ]
        )
    )
    elements.append(header)
    elements.append(Spacer(1, 14))

    company_lines = "<br/>".join(
        [
            f"<b>{quote.company.name}</b>",
            quote.company.address,
            f"Email: {quote.company.email}",
            f"Téléphone: {quote.company.phone}",
            *(
                [f"Site: {quote.company.website}"]
                if quote.company.website
                else []
            ),
        ]
    )
    client_lines = "<br/>".join(
        [
            f"<b>{quote.client.name}</b>",
            quote.client.address,
            f"Email: {quote.client.email}",
            f"Téléphone: {quote.client.phone}",
        ]
    )

    parties = Table(
        [
            [Paragraph("Société", section), Paragraph("Client", section)],
            [Paragraph(company_lines, body), Paragraph(client_lines, body)],
        ],
        colWidths=[240, 240],
    )
    parties.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elements.append(parties)
    elements.append(Spacer(1, 16))

    elements.append(Paragraph("Détails", section))
    table_data = [["Description", "Qté", "PU", "Total"]]
    for item in quote.items:
        table_data.append(
            [
                item.description,
                f"{item.quantity}",
                f"{_format_currency(item.unit_price)} €",
                f"{_format_currency(item.total)} €",
            ]
        )

    table = Table(table_data, colWidths=[260, 50, 80, 80])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), palette["ink"]),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("GRID", (0, 0), (-1, -1), 0.25, palette["border"]),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, palette["soft"]]),
            ]
        )
    )
    elements.append(table)
    elements.append(Spacer(1, 12))

    totals_data = [
        ["Sous-total", f"{_format_currency(subtotal)} €"],
        [f"TVA ({int(quote.tax_rate * 100)}%)", f"{_format_currency(tax_amount)} €"],
        ["Total TTC", f"{_format_currency(total)} €"],
    ]
    totals_table = Table(totals_data, colWidths=[330, 140])
    totals_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("LINEABOVE", (0, -1), (-1, -1), 0.6, palette["ink"]),
            ]
        )
    )
    elements.append(totals_table)

    if quote.notes:
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Notes", section))
        elements.append(Paragraph(quote.notes, body))

    legal_lines = []
    if quote.company.siret:
        legal_lines.append(f"SIRET: {quote.company.siret}")
    if quote.company.vat_number:
        legal_lines.append(f"TVA: {quote.company.vat_number}")
    if quote.company.iban:
        legal_lines.append(f"IBAN: {quote.company.iban}")
    if quote.company.bic:
        legal_lines.append(f"BIC: {quote.company.bic}")

    footer_parts = []
    if legal_lines:
        footer_parts.append(" • ".join(legal_lines))
    if quote.payment_terms:
        footer_parts.append(quote.payment_terms)

    if footer_parts:
        elements.append(Spacer(1, 14))
        elements.append(Paragraph("<br/>".join(footer_parts), foot))

    doc.build(elements)
    return buffer.getvalue()
