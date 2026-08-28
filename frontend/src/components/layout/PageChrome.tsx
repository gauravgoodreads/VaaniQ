/** Shared page chrome for consistent, high-contrast research UI. */

import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

type PageHeaderProps = {
  title: string;
  subtitle?: string;
  children?: ReactNode;
};

export function PageHeader({ title, subtitle, children }: PageHeaderProps) {
  return (
    <header className="mb-8 flex flex-wrap items-end justify-between gap-4">
      <div className="max-w-2xl space-y-3">
        <h1 className="font-[family-name:var(--font-display)] text-4xl tracking-tight text-[var(--fg)] md:text-5xl">
          {title}
        </h1>
        {subtitle ? <p className="text-lg text-[var(--fg-muted)]">{subtitle}</p> : null}
      </div>
      {children}
    </header>
  );
}

type HonestyBannerProps = {
  children: ReactNode;
  className?: string;
};

/** Explicit demo / non-RQ honesty label (proposal honesty rule). */
export function HonestyBanner({ children, className }: HonestyBannerProps) {
  return (
    <aside
      role="note"
      className={cn(
        "rounded-2xl border border-[var(--accent)]/30 bg-[color-mix(in_oklab,var(--accent)_10%,var(--bg-elevated))] px-4 py-3 text-sm text-[var(--fg)]",
        className,
      )}
    >
      {children}
    </aside>
  );
}

type SurfaceProps = {
  children: ReactNode;
  className?: string;
  title?: string;
};

export function Surface({ children, className, title }: SurfaceProps) {
  return (
    <section
      className={cn(
        "rounded-2xl border border-[var(--border)] bg-[var(--bg-elevated)] p-5 text-[var(--fg)] shadow-[0_24px_60px_-48px_rgba(15,28,36,0.55)]",
        className,
      )}
    >
      {title ? (
        <h2 className="mb-4 text-xs uppercase tracking-[0.18em] text-[var(--fg-muted)]">{title}</h2>
      ) : null}
      {children}
    </section>
  );
}

type StatTileProps = {
  label: string;
  value: string;
  hint?: string;
};

export function StatTile({ label, value, hint }: StatTileProps) {
  return (
    <div className="rounded-2xl border border-[var(--border)] bg-[var(--bg-elevated)] p-5">
      <p className="text-xs uppercase tracking-[0.18em] text-[var(--fg-muted)]">{label}</p>
      <p className="mt-2 font-[family-name:var(--font-display)] text-3xl tracking-tight text-[var(--fg)]">
        {value}
      </p>
      {hint ? <p className="mt-1 text-sm text-[var(--fg-muted)]">{hint}</p> : null}
    </div>
  );
}
