"use client";

import { useMemo } from "react";
import CollapsibleSection from "@/components/collapsible-section";

type TrackerRow = {
  symbol: string;
  breakout_date: string;
  entry_price: number;
  current_price: number;
  return_pct: number;
  days_active: number;
};

export default function UltraBreakoutTracker({
  rows,
}: {
  rows: TrackerRow[];
}) {

  const grouped = useMemo(() => {

    const groups: Record<
      string,
      TrackerRow[]
    > = {};

    rows.forEach((row) => {

      const key =
        row.breakout_date;

      if (!groups[key]) {
        groups[key] = [];
      }

      groups[key].push(row);
    });

    return groups;

  }, [rows]);

  return (
    <div className="space-y-4">

      {Object.entries(grouped)
        .sort(
          (a, b) =>
            b[0].localeCompare(a[0])
        )
        .map(
          ([date, breakoutRows]) => (

            <CollapsibleSection
              key={date}
              title={`${date} (${breakoutRows.length})`}
              defaultOpen={
                breakoutRows.length > 0
              }
            >

              <table className="w-full text-sm">

                <thead>
                  <tr>
                    <th className="text-left p-2">
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

                  {breakoutRows.map(
                    (row) => (

                      <tr
                        key={
                          row.symbol
                        }
                      >

                        <td className="p-2 text-primary font-semibold">
                          {row.symbol}
                        </td>

                        <td>
                          ₹
                          {row.entry_price.toFixed(
                            2
                          )}
                        </td>

                        <td>
                          ₹
                          {row.current_price.toFixed(
                            2
                          )}
                        </td>

                        <td
                          className={
                            row.return_pct >= 0
                              ? "text-green-400"
                              : "text-red-400"
                          }
                        >
                          {row.return_pct.toFixed(
                            2
                          )}
                          %
                        </td>

                        <td>
                          {row.days_active}
                        </td>

                      </tr>
                    )
                  )}

                </tbody>

              </table>

            </CollapsibleSection>
          )
        )}

    </div>
  );
}
