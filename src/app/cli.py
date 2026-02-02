from __future__ import annotations

import argparse
from pathlib import Path

from .models import Quote
from .pdf import generate_pdf_bytes


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Générer un devis PDF")
    parser.add_argument("--input", required=True, help="Chemin du fichier JSON")
    parser.add_argument("--output", required=True, help="Chemin du PDF de sortie")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    quote = Quote.model_validate_json(input_path.read_text(encoding="utf-8"))
    pdf_bytes = generate_pdf_bytes(quote)
    output_path.write_bytes(pdf_bytes)


if __name__ == "__main__":
    main()
