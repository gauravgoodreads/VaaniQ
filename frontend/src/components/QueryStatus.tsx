import type { ReactNode } from "react";

type QueryStatusProps = {
  isPending: boolean;
  isError: boolean;
  error?: Error | null;
  empty?: boolean;
  emptyMessage?: string;
  children: ReactNode;
};

/** Shared loading / error / empty states for TanStack Query pages. */
export function QueryStatus({
  isPending,
  isError,
  error,
  empty,
  emptyMessage,
  children,
}: QueryStatusProps) {
  if (isPending) {
    return (
      <p className="text-sm text-[var(--fg-muted)]" role="status">
        Loading…
      </p>
    );
  }
  if (isError) {
    return (
      <p className="text-sm text-[var(--danger)]" role="alert">
        {error?.message ?? "Request failed. Confirm the API is running."}
      </p>
    );
  }
  if (empty) {
    return <p className="text-sm text-[var(--fg-muted)]">{emptyMessage ?? "No data yet."}</p>;
  }
  return <>{children}</>;
}
