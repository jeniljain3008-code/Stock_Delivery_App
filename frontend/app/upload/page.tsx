"use client";

import { useState } from "react";

import {
  uploadDeliveryFile,
  fetchNSEDeliveryData,
} from "@/lib/api";

type NSEPreviewRow = {
  Date: string;
  Symbol: string;
  Open: number;
  High: number;
  Low: number;
  Close: number;
  Volume: number;
  DeliveryQty: number;
  DeliveryPercent: number;
};

export default function UploadPage() {
  const [message, setMessage] = useState("");

  const [tradeDate, setTradeDate] = useState("");

  const [previewRows, setPreviewRows] =
    useState<NSEPreviewRow[]>([]);

  const [loading, setLoading] = useState(false);

  return (
    <div className="mx-auto max-w-6xl space-y-6">

      <h2 className="text-3xl font-bold">
        Upload NSE Delivery Data
      </h2>

      <p className="text-slate-400">
        Upload CSV/Excel manually or fetch NSE
        Delivery Data directly from NSE archives.
      </p>

      {/* Manual Upload */}

      <label className="flex min-h-64 cursor-pointer flex-col items-center justify-center rounded-3xl border border-dashed border-primary/60 bg-card p-8 text-center">

        <span className="text-lg font-semibold">
          Drop CSV/XLSX here or click to browse
        </span>

        <input
          className="hidden"
          type="file"
          accept=".csv,.xlsx,.xls"
          onChange={async (e) => {
            const file = e.target.files?.[0];

            if (!file) return;

            setMessage("Uploading...");

            try {
              const res =
                await uploadDeliveryFile(file);

              setMessage(
                `Loaded ${res.rows_loaded} rows from ${res.file_name}`
              );
            } catch (err) {
              setMessage(
                err instanceof Error
                  ? err.message
                  : "Upload failed"
              );
            }
          }}
        />
      </label>

      {/* NSE Fetch Section */}

      <div className="rounded-3xl border border-border bg-card p-6 space-y-4">

        <h3 className="text-xl font-semibold">
          Fetch NSE Delivery Data
        </h3>

        <p className="text-sm text-slate-400">
          Select a trading date and fetch EQ
          segment delivery data directly from NSE.
        </p>

        <div className="flex flex-wrap gap-4 items-center">

          <input
            type="date"
            value={tradeDate}
            onChange={(e) =>
              setTradeDate(e.target.value)
            }
            className="rounded-lg border border-border bg-background px-4 py-2"
          />

          <button
            disabled={!tradeDate || loading}
            className="rounded-lg bg-blue-600 px-4 py-2 text-white disabled:opacity-50"
            onClick={async () => {

              try {

                setLoading(true);

                setMessage(
                  "Fetching NSE Delivery Data..."
                );

                const result =
                  await fetchNSEDeliveryData(
                    tradeDate
                  );

                setPreviewRows(
                  result.data || []
                );

                setMessage(
                  `Fetched ${result.rows} rows from NSE`
                );

              } catch (err) {

                setMessage(
                  err instanceof Error
                    ? err.message
                    : "Fetch failed"
                );

              } finally {

                setLoading(false);
              }
            }}
          >
            {loading
              ? "Fetching..."
              : "Fetch NSE Delivery Data"}
          </button>

        </div>
      </div>

      {/* Status Message */}

      {message ? (
        <div className="rounded-xl border border-border bg-card p-4">
          {message}
        </div>
      ) : null}

      {/* Preview Table */}

      {previewRows.length > 0 && (

        <div className="rounded-3xl border border-border bg-card p-4">

          <h3 className="mb-4 text-xl font-semibold">
            NSE Data Preview
          </h3>

          <div className="overflow-auto">

            <table className="w-full text-sm">

              <thead>

                <tr className="border-b">

                  <th className="p-2 text-left">
                    Symbol
                  </th>

                  <th className="p-2 text-right">
                    Close
                  </th>

                  <th className="p-2 text-right">
                    Volume
                  </th>

                  <th className="p-2 text-right">
                    Delivery Qty
                  </th>

                  <th className="p-2 text-right">
                    Delivery %
                  </th>

                </tr>

              </thead>

              <tbody>

                {previewRows.map(
                  (row, index) => (

                    <tr
                      key={`${row.Symbol}-${index}`}
                      className="border-b"
                    >

                      <td className="p-2">
                        {row.Symbol}
                      </td>

                      <td className="p-2 text-right">
                        {row.Close}
                      </td>

                      <td className="p-2 text-right">
                        {row.Volume}
                      </td>

                      <td className="p-2 text-right">
                        {row.DeliveryQty}
                      </td>

                      <td className="p-2 text-right">
                        {row.DeliveryPercent}
                      </td>

                    </tr>
                  )
                )}

              </tbody>

            </table>

          </div>

        </div>
      )}

    </div>
  );
}
