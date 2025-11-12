import { useState } from "react";
import { AxiosError } from "axios";
import { uploadPlan } from "../lib/api";

interface Props {
  onUploaded: () => void;
}

export function PlanUploader({ onUploaded }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [coverage, setCoverage] = useState(1.0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) {
      setError("Merci de sélectionner un plan (PDF ou image).");
      return;
    }
    setError(null);
    setIsLoading(true);
    try {
      await uploadPlan(file, coverage);
      setFile(null);
      onUploaded();
    } catch (err) {
      console.error(err);
      if (err instanceof AxiosError) {
        const detail = err.response?.data?.detail;
        setError(
          typeof detail === "string"
            ? detail
            : "Impossible d'envoyer le plan. Vérifiez le backend.",
        );
      } else {
        setError("Impossible d'envoyer le plan. Vérifiez le backend.");
      }
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
    >
      <div>
        <label className="block text-sm font-medium text-slate-600">
          Plan (PDF, PNG, JPG)
        </label>
        <input
          type="file"
          accept=".pdf,.png,.jpg,.jpeg"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className="mt-1 w-full rounded-md border border-dashed border-slate-300 p-3 text-sm"
        />
      </div>

      <div>
          <label className="block text-sm font-medium text-slate-600">
            Couverture (m² par unité)
          </label>
          <input
            type="number"
            min="0.1"
            step="0.1"
            value={coverage}
            onChange={(e) => setCoverage(parseFloat(e.target.value))}
            className="mt-1 w-32 rounded-md border border-slate-300 p-2 text-sm"
          />
        </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <button
        type="submit"
        disabled={isLoading}
        className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {isLoading ? "Analyse en cours..." : "Analyser le plan"}
      </button>
    </form>
  );
}
