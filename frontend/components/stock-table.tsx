export type StockRow = {
  symbol: string;

  close: number;

  sector?: string;

  delivery_surge: number;

  DeliveryPercent?: number;
  
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
  console.log(rows[0]);
  return (
    <div className="overflow-hidden rounded-2xl border border-border bg-card">
      <table className="w-full text-sm">
        <thead className="bg-white/5 text-left text-slate-400">
          <tr>
            <th className="p-3">
              Symbol
            </th>

            <th>
              Price
            </th>

            <th>
              Del %
            </th>  
            <th>
              5D
            </th>

            <th>
              10D
            </th>

            <th>
              30D
            </th>

            <th>
              Score
            </th>

            <th>
              Accumulation
            </th>

            <th>
              Signal
            </th>

            <th>
              Risk
            </th>
          </tr>
        </thead>

        <tbody>
          {rows.map(
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
                      row.DeliveryPercent ??
                      0
                    ).toFixed(1)}
                </td>
                <td>
                  {(
                    row.surge_5d ??
                    0
                  ).toFixed(
                    2
                  )}
                  x
                </td>

                <td>
                  {(
                    row.surge_10d ??
                    0
                  ).toFixed(
                    2
                  )}
                  x
                </td>

                <td>
                  {(
                    row.surge_30d ??
                    0
                  ).toFixed(
                    2
                  )}
                  x
                </td>

                <td>
                  {(
                    row.explosion_score ??
                    0
                  ).toFixed(
                    2
                  )}
                </td>

                <td>
                  {
                    row.accumulation_score
                  }
                </td>

                <td>
                  <span className="rounded-full bg-emerald-500/10 px-2 py-1 text-emerald-300">
                    {
                      row.swing_signal
                    }
                  </span>
                </td>

                <td>
                  {
                    row.risk_rating
                  }
                </td>
              </tr>
            )
          )}
        </tbody>
      </table>
    </div>
  );
}
