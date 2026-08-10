type PageStubProps = {
  title: string;
  description: string;
  roadmapId: string;
};

/** Shared stub body for pages not yet implemented (ROADMAP-054+). */
export function PageStub({ title, description, roadmapId }: PageStubProps) {
  return (
    <section className="space-y-3">
      <h1 className="font-[family-name:var(--font-display)] text-3xl">{title}</h1>
      <p className="max-w-2xl text-[var(--fg-muted)]">{description}</p>
      <p className="text-sm text-[var(--fg-muted)]">
        Deferred: <code>{roadmapId}</code>
      </p>
    </section>
  );
}
