import { KpiCard } from "@/components/kpi-card";
import { StockTable } from "@/components/stock-table";
import { apiGet } from "@/lib/api";

export default async function Dashboard() {
  const data = await apiGet<any>("/api/v1/dashboard/summary");
  return <div className="space-y-8"><section><p className="text-sm uppercase tracking-[0.3em] text-primary">Delivery-first swing intelligence</p><h2 className="mt-2 text-4xl font-bold">Smart-money accumulation dashboard</h2><p className="mt-3 max-w-3xl text-slate-400">Find NSE stocks with unusual delivery expansion before a 5–20% swing move over the next 1–8 weeks.</p></section><div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">{data.kpis.map((kpi: any) => <KpiCard key={kpi.label} {...kpi} />)}</div><section className="grid gap-6 xl:grid-cols-2"><div><h3 className="mb-3 text-xl font-semibold">Top Delivery Surge Stocks</h3><StockTable rows={data.top_delivery_surge} /></div><div><h3 className="mb-3 text-xl font-semibold">Top Breakout Stocks</h3><StockTable rows={data.top_breakouts} /></div></section><section className="rounded-2xl border border-border bg-card p-5"><h3 className="text-xl font-semibold">Market Summary</h3><p className="mt-2 text-slate-300">{data.market_summary}</p></section></div>;
}
