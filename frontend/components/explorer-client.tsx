"use client";

import { useMemo, useState } from "react";
import { StockTable, type StockRow } from "@/components/stock-table";

export default function ExplorerClient({
  rows,
}: {
  rows: StockRow[];
}) {

  const [search, setSearch] = useState("");
  const [sector, setSector] = useState("");
  const [minAccumulation, setMinAccumulation] = useState("");
  const [minBreakout, setMinBreakout] = useState("");

  const filteredRows = useMemo(() => {

    return rows.filter((row) => {

      const matchesSearch =
        !search ||
        row.symbol
          .toLowerCase()
          .includes(search.toLowerCase());

      const matchesSector =
        !sector ||
        (row.sector ?? "")
          .toLowerCase()
          .includes(sector.toLowerCase());

      const matchesAccumulation =
        !minAccumulation ||
        row.accumulation_score >=
          Number(minAccumulation);

      const matchesBreakout =
        !minBreakout ||
        row.breakout_score >=
          Number(minBreakout);

      return (
        matchesSearch &&
        matchesSector &&
        matchesAccumulation &&
        matchesBreakout
      );
    });

  }, [
    rows,
    search,
    sector,
    minAccumulation,
    minBreakout,
  ]);

  return (
    <div className="space-y-6">

      <div className="grid gap-3 md:grid-cols-4">

        <input
          value={search}
          onChange={(e) =>
            setSearch(e.target.value)
          }
          className="rounded-xl border border-border bg-card p-3"
          placeholder="Search stock"
        />

        <input
          value={sector}
          onChange={(e) =>
            setSector(e.target.value)
          }
          className="rounded-xl border border-border bg-card p-3"
          placeholder="Sector"
        />

        <input
          type="number"
          value={minAccumulation}
          onChange={(e) =>
            setMinAccumulation(
              e.target.value
            )
          }
          className="rounded-xl border border-border bg-card p-3"
          placeholder="Min accumulation"
        />

        <input
          type="number"
          value={minBreakout}
          onChange={(e) =>
            setMinBreakout(
              e.target.value
            )
          }
          className="rounded-xl border border-border bg-card p-3"
          placeholder="Min breakout"
        />

      </div>

      <div className="text-sm text-slate-400">
        Showing {filteredRows.length} stocks
      </div>

      <StockTable rows={filteredRows} />

    </div>
  );
}
