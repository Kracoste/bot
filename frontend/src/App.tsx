import { useState } from "react";
import { PlanDetails } from "./components/PlanDetails";
import { PlanList } from "./components/PlanList";
import { PlanUploader } from "./components/PlanUploader";

function App() {
  const [selectedPlanId, setSelectedPlanId] = useState<number>();
  const [refreshFlag, setRefreshFlag] = useState(0);

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-8">
      <div className="mx-auto max-w-6xl space-y-6">
        <header className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-indigo-600">
              SaaS Plans & Prix
            </p>
            <h1 className="text-2xl font-bold text-slate-900">
              Tableaux de surfaces & suivi des prix matériaux
            </h1>
            <p className="text-sm text-slate-500">
              Déposez vos plans, laissez l'IA calculer les surfaces puis interrogez Point.P, Brico
              Dépôt et Castorama en un clic.
            </p>
          </div>
        </header>

        <div className="grid gap-6 md:grid-cols-[1fr_2fr]">
          <div className="space-y-6">
            <PlanUploader
              onUploaded={() => {
                setRefreshFlag((flag) => flag + 1);
              }}
            />
            <PlanList
              selectedId={selectedPlanId}
              onSelect={setSelectedPlanId}
              refreshFlag={refreshFlag}
            />
          </div>
          <PlanDetails planId={selectedPlanId} refreshFlag={refreshFlag} />
        </div>
      </div>
    </div>
  );
}

export default App;
