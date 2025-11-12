import { useEffect, useMemo, useState } from "react";
import {
  PlanDetail,
  PriceRequest,
  createPriceRequest,
  fetchPlanDetail,
  listPriceRequests,
} from "../lib/api";

interface Props {
  planId?: number;
  refreshFlag: number;
}

export function PlanDetails({ planId, refreshFlag }: Props) {
  const [plan, setPlan] = useState<PlanDetail | null>(null);
  const [priceRequests, setPriceRequests] = useState<PriceRequest[]>([]);
  const [query, setQuery] = useState("");
  const [loadingPrices, setLoadingPrices] = useState(false);

  useEffect(() => {
    if (!planId) {
      setPlan(null);
      setPriceRequests([]);
      return;
    }
    fetchPlanDetail(planId).then(setPlan).catch(console.error);
    listPriceRequests(planId).then(setPriceRequests).catch(console.error);
  }, [planId, refreshFlag]);

  const dominantLabel = plan?.dominant_label ?? "libellé inconnu";

  async function handlePriceRequest() {
    if (!planId) return;
    setLoadingPrices(true);
    try {
      await createPriceRequest(planId, query || undefined);
      const results = await listPriceRequests(planId);
      setPriceRequests(results);
      setQuery("");
    } catch (error) {
      console.error(error);
    } finally {
      setLoadingPrices(false);
    }
  }

  if (!planId) {
    return (
      <div className="rounded-xl border border-dashed border-slate-200 bg-white p-8 text-center text-slate-500 shadow-sm">
        Sélectionnez un plan pour afficher les détails.
      </div>
    );
  }

  if (!plan) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-8 text-center shadow-sm">
        Chargement des informations…
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-800">{plan.filename}</h2>
            <p className="text-sm text-slate-500">
              {plan.measurement_count} mesures • {plan.total_area_m2.toFixed(2)} m²
            </p>
          </div>
          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">
            Dominante : {dominantLabel}
          </span>
        </div>

        <div className="mt-4 overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="text-left text-xs uppercase tracking-wide text-slate-500">
                <th className="pb-2">Zone</th>
                <th className="pb-2">Surface (m²)</th>
                <th className="pb-2">Longueur (m)</th>
              </tr>
            </thead>
            <tbody>
              {plan.measurements.map((m, index) => (
                <tr key={`${m.label}-${index}`} className="border-t border-slate-100">
                  <td className="py-2 font-medium text-slate-700">{m.label}</td>
                  <td className="py-2 text-slate-600">
                    {m.area_m2 ? m.area_m2.toFixed(2) : "-"}
                  </td>
                  <td className="py-2 text-slate-600">
                    {m.length_m ? m.length_m.toFixed(2) : "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <h3 className="text-lg font-semibold text-slate-800">Recherche de prix</h3>
        <p className="text-sm text-slate-500">
          Requête proposée : <span className="font-medium">{dominantLabel}</span>
        </p>
        <div className="mt-3 flex flex-wrap gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={`Ex: ${dominantLabel}`}
            className="flex-1 min-w-[200px] rounded-md border border-slate-300 p-2 text-sm"
          />
          <button
            onClick={handlePriceRequest}
            disabled={loadingPrices}
            className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loadingPrices ? "Recherche..." : "Chercher les prix"}
          </button>
        </div>

        <div className="mt-4 space-y-3">
          {priceRequests.map((request) => (
            <div key={request.id} className="rounded-lg border border-slate-100 p-3">
              <p className="text-xs text-slate-500">
                {new Date(request.created_at).toLocaleString()} • requête :{" "}
                <span className="font-medium text-slate-700">{request.query}</span>
              </p>
              <div className="mt-2 grid gap-2 md:grid-cols-3">
                {request.results.map((result, index) => (
                  <a
                    key={`${result.store}-${index}`}
                    href={result.link}
                    target="_blank"
                    rel="noreferrer"
                    className="rounded-md border border-slate-100 p-3 text-sm shadow-sm transition hover:border-indigo-200 hover:shadow"
                  >
                    <p className="font-semibold text-slate-800">{result.store}</p>
                    <p className="text-slate-600">{result.title}</p>
                    <p className="text-indigo-600">
                      {result.price ? `${result.price} €` : "Prix indisponible"}
                    </p>
                    <p className="text-xs text-slate-400">Source: {result.source}</p>
                  </a>
                ))}
              </div>
            </div>
          ))}
          {!priceRequests.length && (
            <p className="text-sm text-slate-500">Aucune recherche pour l'instant.</p>
          )}
        </div>
      </div>
    </div>
  );
}
