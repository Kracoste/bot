import axios from "axios";

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000",
});

export interface Measurement {
  label: string;
  area_m2?: number;
  length_m?: number;
  width_m?: number;
}

export interface PlanSummary {
  id: number;
  filename: string;
  created_at: string;
  measurement_count: number;
  total_area_m2: number;
  total_length_m: number;
  dominant_label?: string | null;
}

export interface PlanDetail extends PlanSummary {
  measurements: Measurement[];
}

export interface PlanCreateResponse extends PlanDetail {
  estimation_total_area_m2: number;
  estimation_units: number;
}

export interface PriceResult {
  store: string;
  title: string;
  link: string;
  price?: string | null;
  source: string;
}

export interface PriceRequest {
  id: number;
  plan_id: number;
  query: string;
  created_at: string;
  results: PriceResult[];
}

export async function listPlans(): Promise<PlanSummary[]> {
  const { data } = await client.get<PlanSummary[]>("/plans");
  return data;
}

export async function uploadPlan(
  file: File,
  coverage: number,
): Promise<PlanCreateResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("coverage", coverage.toString());
  const { data } = await client.post<PlanCreateResponse>("/plans", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function fetchPlanDetail(planId: number): Promise<PlanDetail> {
  const { data } = await client.get<PlanDetail>(`/plans/${planId}`);
  return data;
}

export async function listPriceRequests(planId: number): Promise<PriceRequest[]> {
  const { data } = await client.get<PriceRequest[]>(`/plans/${planId}/prices`);
  return data;
}

export async function createPriceRequest(
  planId: number,
  query?: string,
): Promise<PriceRequest> {
  const { data } = await client.post<PriceRequest>(`/plans/${planId}/prices`, {
    query,
  });
  return data;
}
