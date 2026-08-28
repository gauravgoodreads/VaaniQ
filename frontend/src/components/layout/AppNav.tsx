import { NavLink } from "react-router-dom";

import { cn } from "@/lib/utils";

export type NavItem = {
  to: string;
  label: string;
};

type AppNavProps = {
  items: readonly NavItem[];
  dense?: boolean;
};

/** Primary application navigation. */
export function AppNav({ items, dense = false }: AppNavProps) {
  return (
    <nav
      aria-label={dense ? "Research" : "Primary"}
      className={cn("flex flex-wrap gap-1", dense && "opacity-80")}
    >
      {items.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          className={({ isActive }) =>
            cn(
              "rounded-md transition-colors",
              dense ? "px-2.5 py-1 text-xs" : "px-3 py-2 text-sm",
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
