import { NavLink } from "react-router-dom";

import { cn } from "@/lib/utils";

export type NavItem = {
  to: string;
  label: string;
};

type AppNavProps = {
  items: readonly NavItem[];
};

/** Primary application navigation. */
export function AppNav({ items }: AppNavProps) {
  return (
    <nav aria-label="Primary" className="flex flex-wrap gap-1">
      {items.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          className={({ isActive }) =>
            cn(
              "rounded-md px-3 py-2 text-sm transition-colors",
              isActive
                ? "bg-[var(--accent)] text-[var(--accent-fg)]"
                : "text-[var(--nav-fg)]/80 hover:bg-white/10 hover:text-[var(--nav-fg)]",
            )
          }
          end={item.to === "/"}
        >
          {item.label}
        </NavLink>
      ))}
    </nav>
  );
}
