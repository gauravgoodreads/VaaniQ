import { Link, Outlet } from "react-router-dom";

import { AppNav, type NavItem } from "@/components/layout/AppNav";
import { ThemeToggle } from "@/components/layout/ThemeToggle";
import { useHealth } from "@/hooks/useHealth";

const NAV_ITEMS: readonly NavItem[] = [
  { to: "/", label: "Home" },
  { to: "/dashboard", label: "Dashboard" },
  { to: "/upload", label: "Upload" },
  { to: "/live", label: "Live" },
  { to: "/inference", label: "Inference" },
  { to: "/history", label: "History" },
  { to: "/research-metrics", label: "Metrics" },
  { to: "/experiments", label: "Experiments" },
  { to: "/calibration", label: "Calibration" },
  { to: "/explainability", label: "Explain" },
  { to: "/admin", label: "Admin" },
  { to: "/docs", label: "Docs" },
] as const;

/** App chrome: brand, nav, theme, health chip, page outlet. */
export function AppShell() {
  const health = useHealth();
  const healthLabel = health.isSuccess
    ? `API ${health.data.status}`
    : health.isError
      ? "API offline"
      : "API…";

  return (
    <div className="min-h-screen">
      <header className="border-b border-white/10 bg-[var(--nav)] text-[var(--nav-fg)]">
        <div className="mx-auto flex max-w-6xl flex-col gap-4 px-4 py-4">
          <div className="flex items-center justify-between gap-4">
            <Link to="/" className="font-[family-name:var(--font-display)] text-2xl tracking-tight">
              VaaniQ
            </Link>
            <div className="flex items-center gap-2">
              <span
                className="rounded-full border border-white/20 px-3 py-1 text-xs"
                data-testid="health-chip"
                aria-live="polite"
              >
                {healthLabel}
              </span>
              <ThemeToggle />
            </div>
          </div>
          <AppNav items={NAV_ITEMS} />
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
}
