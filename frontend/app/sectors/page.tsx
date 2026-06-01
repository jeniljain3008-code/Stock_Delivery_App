import { ApiErrorNotice } from "@/components/api-error";
import { apiGetOrFallback } from "@/lib/api";

export const dynamic = "force-dynamic";

type SectorRotationRow = {
  Sector: string;
  average_delivery_increase: number;
  leadership_index: number;
};

export default async function SectorsPage() {
  const { data: rows, error } = await apiGetOrFallback<SectorRotationRow[]>(
    "/api/v1/sectors/rotation",
    [],
  );

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold">Sector Rotation Dashboard</h2>
      <ApiErrorNotice message={error} />
      {rows.length === 0 ? (
        <div className="rounded-2xl border border-border bg-card p-5 text-slate-400">
          No sector rotation data is available yet. Upload NSE delivery data or retry after the backend is online.
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {rows.map((row) => (
            <div key={row.Sector} className="rounded-2xl border border-border bg-card p-5">
              <h3 className="text-xl font-bold">{row.Sector}</h3>
              <p className="mt-2">
                Average delivery increase: {Number(row.average_delivery_increase).toFixed(2)}x
              </p>
              <p>Leadership index: {Number(row.leadership_index).toFixed(1)}</p>
              <div className="mt-4 h-3 rounded-full bg-slate-800">
                <div
                  className="h-3 rounded-full bg-primary"
                  style={{ width: `${Math.min(Number(row.leadership_index), 100)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
