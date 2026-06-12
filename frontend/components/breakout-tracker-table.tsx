"use client";

import { StockRow } from "./stock-table";

export default function BreakoutTrackerTable({
  rows,
}: {
  rows: StockRow[];
}) {

  return (
    <div className="overflow-hidden rounded-2xl border border-border bg-card">

      <table className="w-full text-sm">

        <thead className="bg-white/5">

          <tr>

            <th className="p-3">
              Symbol
            </th>

            <th>
              Entry
            </th>

            <th>
              CMP
            </th>

            <th>
              Return %
            </th>

            <th>
              Days
            </th>

          </tr>

        </thead>

        <tbody>

          {rows.map((row) => {

            const ret =
              row.return_pct ?? 0;

            return (

              <tr
                key={row.symbol}
                className="border-t border-border"
              >

                <td className="p-3 font-semibold text-primary">
                  {row.symbol}
                </td>

                <td>
                  ₹{row.entry_price}
                </td>

                <td>
                  ₹{row.current_price}
                </td>

                <td>

                  <span
                    className={
                      ret > 10
                        ? "text-green-400"
                        : ret > 0
                        ? "text-yellow-400"
                        : "text-red-400"
                    }
                  >

                    {ret.toFixed(2)}%

                  </span>

                </td>

                <td>
                  {row.days_active}
                </td>

              </tr>
            );
          })}

        </tbody>

      </table>

    </div>
  );
}
