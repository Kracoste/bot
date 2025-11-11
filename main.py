from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import load_dotenv

from plan_ai.geometry_calculator import (
    estimate_material_requirements,
    measurements_to_dataframe,
    summarize_measurements,
)
from plan_ai.plan_reader import PlanReader
from price_ai.price_service import PriceLookupService, format_store_prices
from shared.utils import log_info


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyse un plan (PDF / image) puis interroge l'IA prix selon les mesures détectées."
    )
    parser.add_argument(
        "plan_path",
        help="Chemin vers le plan (PDF ou image).",
    )
    parser.add_argument(
        "--price-query",
        help="Requête produit à transmettre à l'IA prix. "
        "Par défaut, on utilise le libellé dominant du plan.",
    )
    parser.add_argument(
        "--per-store-results",
        type=int,
        default=3,
        help="Nombre de résultats Google analysés par magasin (1 à 10).",
    )
    parser.add_argument(
        "--show-table",
        action="store_true",
        help="Affiche le tableau pandas des mesures détectées.",
    )
    parser.add_argument(
        "--coverage",
        type=float,
        default=1.0,
        help="Surface couverte par unité de matériau (m²) pour l'estimation.",
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_arguments()

    reader = PlanReader()
    analysis = reader.read(args.plan_path)
    summary = summarize_measurements(analysis.measurements)

    log_info(
        f"Mesures détectées: {summary.measurement_count} | "
        f"surface totale ~ {summary.total_area_m2:.2f} m² | "
        f"longueur cumulée ~ {summary.total_length_m:.2f} m"
    )

    if args.show_table:
        df = measurements_to_dataframe(analysis.measurements)
        if df.empty:
            log_info("Aucune mesure exploitable trouvée.")
        else:
            print(df.to_string(index=False))

    estimation = estimate_material_requirements(
        analysis.measurements, coverage_per_unit_m2=max(args.coverage, 0.1)
    )
    log_info(
        f"Estimation matériaux: {estimation['estimated_units']:.2f} unités "
        f"pour couvrir {estimation['total_area_m2']:.2f} m²"
    )

    search_query = args.price_query or summary.dominant_label
    if not search_query:
        log_info(
            "Impossible de déduire une requête produit automatique. "
            "Utilisez --price-query pour déclencher la recherche de prix."
        )
        return

    log_info(f"Interrogation de l'IA prix pour: {search_query}")
    service = PriceLookupService()
    store_prices = service.lookup(
        search_query, per_store_results=max(1, min(args.per_store_results, 10))
    )
    print(format_store_prices(store_prices))


if __name__ == "__main__":
    main()
