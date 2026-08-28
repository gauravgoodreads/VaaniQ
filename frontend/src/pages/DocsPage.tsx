import { Link } from "react-router-dom";

import { HonestyBanner, PageHeader, Surface } from "@/components/layout/PageChrome";

const DOCS = [
  {
    title: "Install & run",
    path: "INSTALL_AND_RUN.md",
    blurb: "Fresh-machine setup for backend, frontend, and Docker.",
  },
  {
    title: "Architecture",
    path: "docs/SYSTEM_ARCHITECTURE.md",
    blurb: "C4 containers, API, workers, and data stores.",
  },
  {
    title: "Datasets",
    path: "docs/DATASETS.md",
    blurb: "Kathbath, IndicVoices-R, CV, IndicSynth - licences and manifests.",
  },
  {
    title: "Research & RQs",
    path: "docs/RESEARCH.md",
    blurb: "RQ1-RQ5 narrative, metrics, and honesty rules.",
  },
  {
    title: "Human study",
    path: "docs/HUMAN_STUDY.md",
    blurb: "Listener protocol, clip assignment, export.",
  },
  {
    title: "Known limitations",
    path: "docs/KNOWN_LIMITATIONS.md",
    blurb: "What is demo vs measured - read before claiming results.",
  },
  {
    title: "Capstone proposal",
    path: "docs/source/Capstone_Project_Proposal.md",
    blurb: "Authoritative scope: Hindi, Marathi, Tamil; calibration; human baseline.",
  },
  {
    title: "Completion checklist",
    path: "docs/PROJECT_COMPLETION_CHECKLIST.md",
    blurb: "Maps software to O1-O8 and dissertation chapters.",
  },
] as const;

/** In-app documentation index (ROADMAP-010). */
export function DocsPage() {
  return (
    <section className="vaaniq-enter space-y-8">
      <PageHeader
        title="Docs"
        subtitle="Proposal-aligned guides that ship with the repository. The proposal wins on conflicts."
      />
      <HonestyBanner>
        Paths below are in your local clone under the project root. Open them in the IDE or on GitHub -
        this page is an index, not a rendered markdown viewer.
      </HonestyBanner>
      <div className="grid gap-4 md:grid-cols-2">
        {DOCS.map((doc) => (
          <Surface key={doc.path}>
            <h2 className="font-[family-name:var(--font-display)] text-2xl text-[var(--fg)]">
              {doc.title}
            </h2>
            <p className="mt-2 text-sm text-[var(--fg-muted)]">{doc.blurb}</p>
            <code className="mt-3 block break-all text-xs text-[var(--accent)]">{doc.path}</code>
          </Surface>
        ))}
      </div>
      <Link className="inline-flex text-sm text-[var(--accent)] underline" to="/">
        Back home
      </Link>
    </section>
  );
}
