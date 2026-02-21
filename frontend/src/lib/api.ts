const BASE = "/api";

export async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`);
  return res.json() as Promise<T>;
}

// ── Types matching backend schemas ────────────────────────────────────────
export interface MedicineListItem {
  id: number;
  brand_name: string | null;
  generic_name: string | null;
  dosage_form: string | null;
  route: string | null;
  marketing_status: string | null;
  product_ndc: string | null;
  manufacturer_name: string | null;
}

export interface Ingredient {
  id: number;
  name: string | null;
  strength: string | null;
  unii: string | null;
}

export interface MedicineDetail extends MedicineListItem {
  rxcui: string | null;
  created_at: string | null;
  ingredients: Ingredient[];
}

export interface SupplierListItem {
  id: number;
  name: string;
  email: string | null;
  phone: string | null;
  is_active: boolean;
}

export interface MedicineWithSuppliers extends MedicineDetail {
  suppliers: SupplierListItem[];
}

export interface SupplierWithMedicines extends SupplierListItem {
  medicines: MedicineListItem[];
}

export interface Paginated<T> {
  total: number;
  page: number;
  per_page: number;
  items: T[];
}

// ── API functions ─────────────────────────────────────────────────────────
export const getMedicines = (page = 1, perPage = 20) =>
  fetchJson<Paginated<MedicineListItem>>(
    `/medicines?page=${page}&per_page=${perPage}`
  );

export const searchMedicines = (q: string, page = 1, perPage = 20) =>
  fetchJson<Paginated<MedicineListItem>>(
    `/medicines/search?q=${encodeURIComponent(q)}&page=${page}&per_page=${perPage}`
  );

export const getMedicineDetail = (id: number) =>
  fetchJson<MedicineDetail>(`/medicines/${id}`);

export const getMedicineSuppliers = (id: number) =>
  fetchJson<MedicineWithSuppliers>(`/medicines/${id}/suppliers`);

export const getSuppliers = (page = 1, perPage = 20) =>
  fetchJson<Paginated<SupplierListItem>>(
    `/suppliers?page=${page}&per_page=${perPage}`
  );

export const getSupplierWithMedicines = (id: number) =>
  fetchJson<SupplierWithMedicines>(`/suppliers/${id}`);
