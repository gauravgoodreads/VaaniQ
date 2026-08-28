import { Link, Outlet, useLocation } from "react-router-dom";

import { AppNav, type NavItem } from "@/components/layout/AppNav";
import { ThemeToggle } from "@/components/layout/ThemeToggle";
import { useHealth } from "@/hooks/useHealth";
import { cn } from "@/lib/utils";

const PRIMARY_NAV: readonly NavItem[] = [
  { to: "/", label: "Home" },
  { to: "/upload", label: "Upload" },
  { to: "/live", label: "Live" },
  { to: "/inference", label: "Inference" },
  { to: "/dashboard", label: "Dashboard" },
  { to: "/history", label: "History" },
] as const;

const RESEARCH_NAV: readonly NavItem[] = [
  { to: "/research-metrics", label: "Metrics" },
  { to: "/experiments", label: "Experiments" },
  { to: "/calibration", label: "Calibration" },
  { to: "/explainability", label: "Explain" },
  { to: "/human-study", label: "Human study" },
  { to: "/datasets", label: "Datasets" },
  { to: "/admin", label: "Admin" },
  { to: "/docs", label: "Docs" },
] as const;

/** App chrome: brand, nav, theme, health chip, page outlet. */
export function AppShell() {
  const health = useHealth();
  const { pathname } = useLocation();
  const isLanding = pathname === "/";
  const healthLabel = health.isSuccess
    ? `API ${health.data.status}`
    : health.isError
      ? "API offline"
      : "API…";

  return (
    <div className="min-h-screen">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:m-3 focus:rounded-md focus:bg-[var(--accent)] focus:px-4 focus:py-2 focus:text-[var(--accent-fg)]"
      >
        Skip to content
      </a>
      <header
        className={cn(
          "sticky top-0 z-40 border-b backdrop-blur-xl",
          isLanding
            ? "border-white/10 bg-[#071216]/80 text-[#e8f2f0]"
            : "border-[var(--border)]/80 bg-[var(--nav)]/95 text-[var(--nav-fg)]",
        )}
      >
        <div className="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-3">
          <div className="flex items-center justify-between gap-4">
            <Link
              to="/"
              className="font-[family-name:var(--font-display)] text-2xl tracking-tight"
            >
              VaaniQ
            </Link>
            <div className="flex items-center gap-2">
              <span
                className={cn(
                  "inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs",
                  health.isSuccess
                    ? "border-emerald-400/30 text-emerald-200"
                    : "border-white/20 text-white/70",
                )}
                data-testid="health-chip"
                aria-live="polite"
              >
                <span
                  className={cn(
                    "h-1.5 w-1.5 rounded-full",
                    health.isSuccess ? "bg-emerald-400 vaaniq-pulse-dot" : "bg-amber-400",
                  )}
                  aria-hidden
                />
                {healthLabel}
              </span>
              <ThemeToggle />
            </div>
          </div>
          <AppNav items={PRIMARY_NAV} />
          <AppNav items={RESEARCH_NAV} dense />
        </div>
      </header>
      <main
        id="main-content"
        className={cn(
          "vaaniq-enter mx-auto max-w-6xl px-4",
          isLanding ? "py-0" : "py-8",
        )}
      >
        <Outlet />
      </main>
    </div>
  );
}
