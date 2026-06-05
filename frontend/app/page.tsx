import { ApiErrorNotice } from "@/components/api-error";
import { KpiCard } from "@/components/kpi-card";
import { StockTable, type StockRow } from "@/components/stock-table";
import { apiGetOrFallback } from "@/lib/api";

export const dynamic = "force-dynamic";

type DashboardSummary = {
  kpis: Array<{
    label: string;
    value: string | number;
    change?: number | null;
  }>;

  top_delivery_surge: StockRow[];
  top_breakouts: StockRow[];

  exploded_stocks: StockRow[];
  ready_to_explode: StockRow[];
  preparing_to_explode: StockRow[];

  market_summary: string;
};
const fallbackDashboard: DashboardSummary = {
  kpis: [
    { label: "Total Stocks Analyzed", value: 0 },
    { label: "Stocks in Accumulation", value: 0 },
    { label: "Stocks in Distribution", value: 0 },
    { label: "Gold Stock Candidates", value: 0 },
  ],

  top_delivery_surge: [],
  top_breakouts: [],

  exploded_stocks: [],
  ready_to_explode: [],
  preparing_to_explode: [],

  market_summary:
    "Backend data is unavailable. Upload data or retry after the API is online.",
};

export default async function Dashboard() {
  const { data, error } = await apiGetOrFallback<DashboardSummary>(
    "/api/v1/dashboard/summary",
    fallbackDashboard,
  );

  return (
    <div className="space-y-8">
      <section>
        <p className="text-sm uppercase tracking-[0.3em] text-primary">
          Delivery-first swing intelligence
        </p>
        <h2 className="mt-2 text-4xl font-bold">Smart-money accumulation dashboard</h2>
        <p className="mt-3 max-w-3xl text-slate-400">
          Find NSE stocks with unusual delivery expansion before a 5–20% swing move over the next 1–8 weeks.
        </p>
      </section>
      <ApiErrorNotice message={error} />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {data.kpis.map((kpi) => (
          <KpiCard key={kpi.label} {...kpi} />
        ))}
      </div>
      <section className="grid gap-6 xl:grid-cols-2">
        <div>
          <h3 className="mb-3 text-xl font-semibold">Top Delivery Surge Stocks</h3>
          <StockTable rows={data.top_delivery_surge} />
        </div>
        <div>
          <h3 className="mb-3 text-xl font-semibold">Top Breakout Stocks</h3>
          <StockTable rows={data.top_breakouts} />
        </div>
      </section>
      <section className="space-y-8">
      
        <div>
          <h3 className="mb-3 text-xl font-semibold">
            🚀 Exploded Stocks
          </h3>
      
          <StockTable
            rows={data.exploded_stocks}
          />
        </div>
      
        <div>
          <h3 className="mb-3 text-xl font-semibold">
            🔥 Ready To Explode
          </h3>
      
          <StockTable
            rows={data.ready_to_explode}
          />
        </div>
      
        <div>
          <h3 className="mb-3 text-xl font-semibold">
            👀 Preparing To Explode
          </h3>
      
          <StockTable
            rows={data.preparing_to_explode}
          />
        </div>
      
      </section>
      <section className="rounded-2xl border border-border bg-card p-5">
        <h3 className="text-xl font-semibold">Market Summary</h3>
        <p className="mt-2 text-slate-300">{data.market_summary}</p>
      </section>
    </div>
  );
}
