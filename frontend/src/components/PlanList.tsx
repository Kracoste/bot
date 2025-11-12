import { useEffect, useState } from "react";
import { listPlans, PlanSummary } from "../lib/api";

interface Props {
  selectedId?: number;
  onSelect: (planId: number) => void;
  refreshFlag: number;
}

export function PlanList({ selectedId, onSelect, refreshFlag }: Props) {
  const [plans, setPlans] = useState<PlanSummary[]>([]);

  useEffect(() => {
    listPlans().then(setPlans).catch(console.error);
  }, [refreshFlag]);

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-800">Plans analysés</h2>
      <ul className="mt-3 space-y-2">
        {plans.map((plan) => (
          <li key={plan.id}>
            <button
              onClick={() => onSelect(plan.id)}
              className={`w-full rounded-lg border p-3 text-left text-sm ${
                selectedId === plan.id
                  ? "border-indigo-500 bg-indigo-50"
                  : "border-slate-200 hover:border-indigo-300"
              }`}
            >
              <p className="font-medium text-slate-800">{plan.filename}</p>
              <p className="text-xs text-slate-500">
                {new Date(plan.created_at).toLocaleString()} • {plan.measurement_count} mesures •{" "}
                {plan.total_area_m2.toFixed(2)} m²
              </p>
            </button>
          </li>
        ))}
        {!plans.length && (
          <li className="text-sm text-slate-500">
            Aucun plan enregistré pour le moment.
          </li>
        )}
      </ul>
    </div>
  );
}
