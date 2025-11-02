from __future__ import annotations

import argparse
from dotenv import load_dotenv

from price_service import PriceLookupService, format_store_prices


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Recherche un produit dans les catalogues Leroy Merlin, Brico Dépôt et "
            "Castorama via l'API Google Custom Search."
        )
    )
    parser.add_argument(
        "product",
        help="Nom du produit recherché (ex: 'perceuse sans fil Makita').",
    )
    parser.add_argument(
        "--per-store-results",
        type=int,
        default=3,
        help="Nombre de résultats Google à analyser par magasin (1 à 10).",
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_arguments()
    service: PriceLookupService
    try:
        service = PriceLookupService()
    except ValueError as error:
        raise SystemExit(error) from error

    product = args.product
    store_prices = service.lookup(
        product, per_store_results=max(1, min(args.per_store_results, 10))
    )
    print(f"Résultats pour: {product}")
    print("=" * (12 + len(product)))
    print(format_store_prices(store_prices))


if __name__ == "__main__":
    main()
