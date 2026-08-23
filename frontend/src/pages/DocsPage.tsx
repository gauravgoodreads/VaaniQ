import { Link } from "react-router-dom";

/** In-app documentation index (ROADMAP-010). */
export function DocsPage() {
  const links = [
    ["/docs/FINAL_ARCHITECTURE.md", "Architecture"],
    ["/docs/EXPERIMENTS.md", "Experiments"],
    ["/docs/CALIBRATION.md", "Calibration"],
    ["/docs/HUMAN_STUDY.md", "Human study"],
    ["/docs/DEPLOYMENT.md", "Deployment"],
    ["/docs/PROJECT_COMPLETION_CHECKLIST.md", "Completion checklist"],
  ] as const;
  return (
    <section className="vaaniq-enter space-y-4">
      <h1 className="font-[family-name:var(--font-display)] text-3xl">Docs</h1>
      <p className="max-w-2xl text-[var(--fg-muted)]">
        Guides live in the repository <code>docs/</code> folder. The proposal is authoritative.
      </p>
      <ul className="list-disc space-y-1 pl-5 text-sm">
        {links.map(([href, label]) => (
          <li key={href}>
            <code>{href}</code> — {label}
          </li>
        ))}
      </ul>
      <Link className="underline" to="/">
        Back home
      </Link>
    </section>
  );
}
