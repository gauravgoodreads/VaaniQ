import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { useState } from "react";
import { BrowserRouter } from "react-router-dom";

import { AppErrorBoundary } from "@/app/ErrorBoundary";

type AppProvidersProps = {
  children: ReactNode;
};

/** Composition root for router, query client, and error boundary. */
export function AppProviders({ children }: AppProvidersProps) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 10_000,
            refetchOnWindowFocus: false,
          },
        },
      }),
  );

  return (
    <AppErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>{children}</BrowserRouter>
      </QueryClientProvider>
    </AppErrorBoundary>
  );
}
