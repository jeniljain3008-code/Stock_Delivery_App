export function ApiErrorNotice({ message }: { message: string | null }) {
  if (!message) return null;

  return (
    <div className="rounded-2xl border border-amber-500/40 bg-amber-500/10 p-4 text-sm text-amber-100">
      <p className="font-semibold">Live backend data is temporarily unavailable.</p>
      <p className="mt-1 text-amber-100/80">
        Showing an empty fallback state so the app can still build and load. Details: {message}
      </p>
    </div>
  );
}
