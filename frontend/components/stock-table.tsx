"use client";

import {
  useMemo,
  useState,
} from "react";

export type StockRow = {
  symbol: string;

  close: number;

  sector?: string;

  delivery_surge: number;

  delivery_percent?: number;

  surge_5d?: number;
  surge_10d?: number;
  surge_30d?: number;

  explosion_score?: number;

  accumulation_score: number;

  breakout_score: number;

  risk_rating: string;

  swing_signal: string;
};

export function StockTable({
  rows,
}: {
  rows: StockRow[];
}) {

  const [
    sortField,
    setSortField,
  ] = useState<keyof StockRow>(
    "surge_30d"
  );

  const [
    sortDirection,
    setSortDirection,
  ] = useState<"asc" | "desc">(
    "desc"
  );

  const handleSort = (
    field: keyof StockRow
  ) => {

    if (
      sortField === field
    ) {

      setSortDirection(
        sortDirection === "asc"
          ? "desc"
          : "asc"
      );

      return;
    }

    setSortField(
      field
    );

    setSortDirection(
      "desc"
    );
  };

  const sortedRows =
    useMemo(() => {

      return [...rows].sort(
        (a, b) => {

          const aVal =
            a[sortField] ?? 0;

          const bVal =
            b[sortField] ?? 0;

          if (
            typeof aVal ===
              "string" &&
            typeof bVal ===
              "string"
          ) {

            return sortDirection ===
              "asc"
              ? aVal.localeCompare(
                  bVal
                )
              : bVal.localeCompare(
                  aVal
                );
          }

          return sortDirection ===
            "asc"
            ? Number(aVal) -
                Number(bVal)
            : Number(bVal) -
                Number(aVal);
        }
      );

    }, [
      rows,
      sortField,
      sortDirection,
    ]);

  const arrow = (
    field: keyof StockRow
  ) => {

    if (
      sortField !== field
    )
      return "";

    return sortDirection ===
      "asc"
      ? " ↑"
      : " ↓";
  };

  const copySymbols =
    async () => {

      const symbols =
        sortedRows
          .map(
            (row) =>
              row.symbol
          )
          .join(",");

      await navigator.clipboard.writeText(
        symbols
      );

      alert(
        `${sortedRows.length} symbols copied`
      );
    };

  const copyTradingViewWatchlist =
    async () => {

      const symbols =
        sortedRows
          .map(
            (row) =>
              `NSE:${row.symbol}`
          )
          .join(",");

      await navigator.clipboard.writeText(
        symbols
      );

      alert(
        `TradingView watchlist copied (${sortedRows.length} symbols)`
      );
    };

  return (

    <div className="space-y-3">

      <div className="flex flex-wrap gap-2">

        <button
          onClick={copySymbols}
          className="rounded-lg bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          📋 Copy Symbols
        </button>

        <button
          onClick={
            copyTradingViewWatchlist
          }
          className="rounded-lg bg-emerald-600 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-700"
        >
          📈 TradingView Watchlist
        </button>

        <div className="flex items-center text-sm text-slate-400">
          {sortedRows.length} stocks
        </div>

      </div>

      <div className="overflow-hidden rounded-2xl border border-border bg-card">

        <table className="w-full text-sm">

          <thead className="bg-white/5 text-left text-slate-400">
            <tr>

              <th
                className="p-3 cursor-pointer"
                onClick={() =>
                  handleSort(
                    "symbol"
                  )
                }
              >
                Symbol
                {arrow("symbol")}
              </th>

              <th
                className="cursor-pointer"
                onClick={() =>
                  handleSort(
                    "close"
                  )
                }
              >
                Price
                {arrow("close")}
              </th>

              <th
                className="cursor-pointer"
                onClick={() =>
                  handleSort(
                    "delivery_percent"
                  )
                }
              >
                Del %
                {arrow(
                  "delivery_percent"
                )}
              </th>

              <th
                className="cursor-pointer"
                onClick={() =>
                  handleSort(
                    "surge_5d"
                  )
                }
              >
                5D
                {arrow("surge_5d")}
              </th>

              <th
                className="cursor-pointer"
                onClick={() =>
                  handleSort(
                    "surge_10d"
                  )
                }
              >
                10D
                {arrow("surge_10d")}
              </th>

              <th
                className="cursor-pointer"
                onClick={() =>
                  handleSort(
                    "surge_30d"
                  )
                }
              >
                30D
                {arrow("surge_30d")}
              </th>

              <th
                className="cursor-pointer"
                onClick={() =>
                  handleSort(
                    "explosion_score"
                  )
                }
              >
                Score
                {arrow(
                  "explosion_score"
                )}
              </th>

              <th
                className="cursor-pointer"
                onClick={() =>
                  handleSort(
                    "accumulation_score"
                  )
                }
              >
                Accumulation
                {arrow(
                  "accumulation_score"
                )}
              </th>

              <th>
                Signal
              </th>

              <th
                className="cursor-pointer"
                onClick={() =>
                  handleSort(
                    "risk_rating"
                  )
                }
              >
                Risk
                {arrow(
                  "risk_rating"
                )}
              </th>

            </tr>
          </thead>

          <tbody>
            {sortedRows.map(
              (row) => (
                <tr
                  key={
                    row.symbol
                  }
                  className="border-t border-border"
                >
                  <td className="p-3 font-semibold text-primary">
                    {row.symbol}
                  </td>

                  <td>
                    ₹
                    {row.close}
                  </td>

                  <td>
                    {(
                      row.delivery_percent ??
                      0
                    ).toFixed(1)}
                  </td>

                  <td>
                    {(
                      row.surge_5d ??
                      0
                    ).toFixed(2)}
                    x
                  </td>

                  <td>
                    {(
                      row.surge_10d ??
                      0
                    ).toFixed(2)}
                    x
                  </td>

                  <td>
                    {(
                      row.surge_30d ??
                      0
                    ).toFixed(2)}
                    x
                  </td>

                  <td>
                    {(
                      row.explosion_score ??
                      0
                    ).toFixed(2)}
                  </td>

                  <td>
                    {row.accumulation_score}
                  </td>

                  <td>
                    <span className="rounded-full bg-emerald-500/10 px-2 py-1 text-emerald-300">
                      {row.swing_signal}
                    </span>
                  </td>

                  <td>
                    {row.risk_rating}
                  </td>

                </tr>
              )
            )}
          </tbody>

        </table>

      </div>

    </div>

  );
}
