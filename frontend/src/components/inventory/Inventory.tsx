import { useEffect, useState, useCallback } from "react";
import {
  getMedicines,
  searchMedicines,
  getMedicineSuppliers,
  type MedicineListItem,
  type MedicineWithSuppliers,
  type Paginated,
} from "../../lib/api";
import {
  Search,
  ChevronLeft,
  ChevronRight,
  Pill,
  X,
  Truck,
} from "lucide-react";

const Inventory = () => {
  // ── state ─────────────────────────────────────────────────────────────
  const [data, setData] = useState<Paginated<MedicineListItem> | null>(null);
  const [page, setPage] = useState(1);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState<MedicineWithSuppliers | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  // ── fetch list ────────────────────────────────────────────────────────
  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = query.trim()
        ? await searchMedicines(query.trim(), page)
        : await getMedicines(page);
      setData(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [page, query]);

  useEffect(() => {
    load();
  }, [load]);

  // ── search handler (reset to page 1) ─────────────────────────────────
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    load();
  };

  // ── open detail panel ─────────────────────────────────────────────────
  const openDetail = async (med: MedicineListItem) => {
    setDetailLoading(true);
    try {
      const detail = await getMedicineSuppliers(med.id);
      setSelected(detail);
    } catch (e) {
      console.error(e);
    } finally {
      setDetailLoading(false);
    }
  };

  const totalPages = data ? Math.ceil(data.total / data.per_page) : 0;

  return (
    <div className="flex flex-1 gap-4 p-5 overflow-hidden">
      {/* ── LEFT: Medicine list ─────────────────────────────────────────── */}
      <div className="flex flex-col flex-1 min-w-0">
        {/* search bar */}
        <form onSubmit={handleSearch} className="flex gap-2 mb-4">
          <div className="relative flex-1">
            <Search
              size={16}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
            />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search medicines by name…"
              className="w-full pl-9 pr-3 py-2 rounded-lg border border-gray-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 transition"
          >
            Search
          </button>
        </form>

        {/* table */}
        <div className="flex-1 overflow-auto rounded-xl border border-gray-200 bg-white">
          {loading ? (
            <div className="flex items-center justify-center h-40 text-gray-400">
              Loading…
            </div>
          ) : (
            <table className="w-full text-sm">
              <thead className="bg-gray-50 sticky top-0">
                <tr className="text-left text-gray-500 text-xs uppercase tracking-wider">
                  <th className="px-4 py-3">Brand Name</th>
                  <th className="px-4 py-3">Generic Name</th>
                  <th className="px-4 py-3">Form</th>
                  <th className="px-4 py-3">Route</th>
                  <th className="px-4 py-3">NDC</th>
                  <th className="px-4 py-3">Manufacturer</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {data?.items.map((med) => (
                  <tr
                    key={med.id}
                    onClick={() => openDetail(med)}
                    className={`cursor-pointer hover:bg-blue-50 transition ${
                      selected?.id === med.id ? "bg-blue-50" : ""
                    }`}
                  >
                    <td className="px-4 py-3 font-medium text-gray-900">
                      {med.brand_name ?? "—"}
                    </td>
                    <td className="px-4 py-3 text-gray-600">
                      {med.generic_name ?? "—"}
                    </td>
                    <td className="px-4 py-3 text-gray-600">
                      {med.dosage_form ?? "—"}
                    </td>
                    <td className="px-4 py-3 text-gray-600">
                      {med.route ?? "—"}
                    </td>
                    <td className="px-4 py-3 text-gray-500 font-mono text-xs">
                      {med.product_ndc ?? "—"}
                    </td>
                    <td className="px-4 py-3 text-gray-600">
                      {med.manufacturer_name ?? "—"}
                    </td>
                  </tr>
                ))}
                {data?.items.length === 0 && (
                  <tr>
                    <td colSpan={6} className="text-center py-12 text-gray-400">
                      No medicines found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </div>

        {/* pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between mt-3 text-sm text-gray-500">
            <span>
              Page {data?.page} of {totalPages} · {data?.total} results
            </span>
            <div className="flex gap-1">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
                className="p-1 rounded hover:bg-gray-100 disabled:opacity-30"
              >
                <ChevronLeft size={18} />
              </button>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
                className="p-1 rounded hover:bg-gray-100 disabled:opacity-30"
              >
                <ChevronRight size={18} />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* ── RIGHT: Detail panel ────────────────────────────────────────── */}
      {(selected || detailLoading) && (
        <div className="w-96 shrink-0 rounded-xl border border-gray-200 bg-white overflow-auto p-5">
          {detailLoading ? (
            <div className="flex items-center justify-center h-40 text-gray-400">
              Loading detail…
            </div>
          ) : selected ? (
            <>
              {/* header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-2">
                  <div className="h-9 w-9 rounded-lg bg-blue-100 flex items-center justify-center">
                    <Pill size={18} className="text-blue-600" />
                  </div>
                  <div>
                    <h2 className="font-semibold text-gray-900 leading-tight">
                      {selected.brand_name ?? "Unknown"}
                    </h2>
                    <p className="text-xs text-gray-500">
                      {selected.generic_name}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setSelected(null)}
                  className="p-1 rounded hover:bg-gray-100"
                >
                  <X size={16} />
                </button>
              </div>

              {/* info grid */}
              <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm mb-5">
                <dt className="text-gray-500">Form</dt>
                <dd>{selected.dosage_form ?? "—"}</dd>
                <dt className="text-gray-500">Route</dt>
                <dd>{selected.route ?? "—"}</dd>
                <dt className="text-gray-500">Status</dt>
                <dd>{selected.marketing_status ?? "—"}</dd>
                <dt className="text-gray-500">NDC</dt>
                <dd className="font-mono text-xs">
                  {selected.product_ndc ?? "—"}
                </dd>
                <dt className="text-gray-500">RxCUI</dt>
                <dd className="font-mono text-xs">{selected.rxcui ?? "—"}</dd>
              </dl>

              {/* ingredients */}
              {selected.ingredients.length > 0 && (
                <div className="mb-5">
                  <h3 className="text-xs uppercase tracking-wider text-gray-500 mb-2">
                    Active Ingredients
                  </h3>
                  <ul className="space-y-1">
                    {selected.ingredients.map((ing) => (
                      <li
                        key={ing.id}
                        className="flex justify-between text-sm bg-gray-50 px-3 py-1.5 rounded"
                      >
                        <span>{ing.name ?? "—"}</span>
                        <span className="text-gray-500">
                          {ing.strength ?? ""}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* suppliers */}
              <div>
                <h3 className="text-xs uppercase tracking-wider text-gray-500 mb-2 flex items-center gap-1">
                  <Truck size={14} /> Suppliers
                </h3>
                {selected.suppliers.length === 0 ? (
                  <p className="text-sm text-gray-400">
                    No supplier data available.
                  </p>
                ) : (
                  <ul className="space-y-2">
                    {selected.suppliers.map((sup) => (
                      <li
                        key={sup.id}
                        className="flex items-center justify-between bg-gray-50 px-3 py-2 rounded text-sm"
                      >
                        <span className="font-medium text-gray-800">
                          {sup.name}
                        </span>
                        <span
                          className={`text-xs px-2 py-0.5 rounded-full ${
                            sup.is_active
                              ? "bg-green-100 text-green-700"
                              : "bg-red-100 text-red-700"
                          }`}
                        >
                          {sup.is_active ? "Active" : "Inactive"}
                        </span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </>
          ) : null}
        </div>
      )}
    </div>
  );
};

export default Inventory;
