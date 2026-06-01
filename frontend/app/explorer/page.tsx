import { ApiErrorNotice } from "@/components/api-error";
import { StockTable, type StockRow } from "@/components/stock-table";
import { apiGetOrFallback } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function ExplorerPage() {
  const { data: rows, error } = await apiGetOrFallback<StockRow[]>("/api/v1/stocks", []);

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold">Stock Explorer</h2>
      <ApiErrorNotice message={error} />
      <div className="grid gap-3 md:grid-cols-5">
        <input className="rounded-xl border border-border bg-card p-3" placeholder="Search stock" />
        <input className="rounded-xl border border-border bg-card p-3" placeholder="Sector" />
        <input className="rounded-xl border border-border bg-card p-3" placeholder="Market cap" />
        <input className="rounded-xl border border-border bg-card p-3" placeholder="Min accumulation" />
        <input className="rounded-xl border border-border bg-card p-3" placeholder="Min breakout" />
      </div>
      {rows.length === 0 ? (
        <div className="rounded-2xl border border-border bg-card p-5 text-slate-400">
          No stock explorer data is available yet. Upload delivery data or retry after the backend is online.
        </div>
      ) : (
        <StockTable rows={rows} />
      )}
    </div>
  );
}
