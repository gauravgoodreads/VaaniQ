import type { ReactNode } from "react";
import { ErrorBoundary as ReactErrorBoundary, type FallbackProps } from "react-error-boundary";

type AppErrorBoundaryProps = {
  children: ReactNode;
};

function Fallback({ error, resetErrorBoundary }: FallbackProps) {
  const message = error instanceof Error ? error.message : "Unknown error";
  return (
    <div className="mx-auto max-w-lg px-4 py-16 text-center">
      <h1 className="font-[family-name:var(--font-display)] text-2xl">Something went wrong</h1>
      <p className="mt-2 text-[var(--fg-muted)]">{message}</p>
      <button
        type="button"
        className="mt-6 rounded-md bg-[var(--accent)] px-4 py-2 text-[var(--accent-fg)]"
        onClick={resetErrorBoundary}
      >
        Try again
      </button>
    </div>
  );
}

/** Function-component error boundary via react-error-boundary. */
export function AppErrorBoundary({ children }: AppErrorBoundaryProps) {
  return (
    <ReactErrorBoundary
      FallbackComponent={Fallback}
      onReset={() => {
        window.location.assign("/");
      }}
    >
      {children}
    </ReactErrorBoundary>
  );
}
