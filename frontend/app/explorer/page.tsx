import { ApiErrorNotice } from "@/components/api-error";
import ExplorerClient from "@/components/explorer-client";
import { type StockRow } from "@/components/stock-table";
import { apiGetOrFallback } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function ExplorerPage() {

  const {
    data: rows,
    error,
  } =
    await apiGetOrFallback<StockRow[]>(
      "/api/v1/stocks",
      []
    );

  return (
    <div className="space-y-6">

      <h2 className="text-3xl font-bold">
        Stock Explorer
      </h2>

      <ApiErrorNotice
        message={error}
      />

      {rows.length === 0 ? (
        <div className="rounded-2xl border border-border bg-card p-5 text-slate-400">
          No stock explorer data is available yet.
        </div>
      ) : (
        <ExplorerClient
          rows={rows}
        />
      )}

    </div>
  );
}
