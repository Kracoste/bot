from __future__ import annotations

import argparse
import sys
from typing import Optional

from dotenv import load_dotenv

from price_service import (
    PriceLookupService,
    format_store_prices,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Démarre un mode conversationnel pour demander des prix chez "
            "Leroy Merlin, Brico Dépôt et Castorama."
        )
    )
    parser.add_argument(
        "--per-store-results",
        type=int,
        default=3,
        help="Nombre de résultats Google analysés par magasin (1 à 10).",
    )
    return parser.parse_args()


def main() -> int:
    load_dotenv()
    args = parse_arguments()

    try:
        service = PriceLookupService()
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1

    per_store_results = max(1, min(args.per_store_results, 10))
    print("💬 Mode chat prix bricolage")
    print("Entrez un produit (ex: 'sac de ciment 25kg'). Tapez 'quit' pour sortir.")

    while True:
        try:
            query = input("Produit> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAu revoir !")
            break

        if not query:
            continue

        lowered = query.lower()
        if lowered in {"quit", "exit", "q"}:
            print("À bientôt !")
            break
        if lowered in {"help", "?"}:
            print("Utilisez 'set results <n>' pour changer le nombre de résultats Google (1-10).")
            continue

        if lowered.startswith("set results"):
            parts = lowered.split()
            if len(parts) == 3 and parts[1] == "results":
                try:
                    value = int(parts[2])
                except ValueError:
                    print("Valeur invalide. Merci de saisir un nombre entre 1 et 10.")
                    continue
                per_store_results = max(1, min(value, 10))
                print(f"Analyse désormais {per_store_results} résultat(s) Google par magasin.")
            else:
                print("Commande inconnue. Exemple : set results 5")
            continue

        try:
            store_prices = service.lookup(
                query, per_store_results=per_store_results
            )
        except RuntimeError as error:
            print(f"❌ {error}")
            continue

        print(f"Résultats pour: {query}")
        print("=" * (12 + len(query)))
        print(format_store_prices(store_prices))

    return 0


if __name__ == "__main__":
    sys.exit(main())
