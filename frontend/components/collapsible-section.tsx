"use client";

import { useState } from "react";

export default function CollapsibleSection({
  title,
  children,
  defaultOpen = true,
}: {
  title: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
}) {

  const [open, setOpen] =
    useState(defaultOpen);

  return (
    <div className="rounded-2xl border border-border bg-card p-4">

      <button
        onClick={() =>
          setOpen(!open)
        }
        className="flex w-full items-center justify-between text-left text-xl font-semibold"
      >
        <span>
          {title}
        </span>

        <span>
          {open
            ? "▼"
            : "▶"}
        </span>
      </button>

      {open && (
        <div className="mt-4">
          {children}
        </div>
      )}

    </div>
  );
}
