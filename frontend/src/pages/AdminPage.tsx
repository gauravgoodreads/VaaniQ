import { useQuery } from "@tanstack/react-query";

import { getJson } from "@/api/client";
import { QueryStatus } from "@/components/QueryStatus";
import { HonestyBanner, PageHeader, StatTile, Surface } from "@/components/layout/PageChrome";

type AdminStatus = {
  status: string;
  env: string;
  hardware: Record<string, string>;
  git_sha: string;
};

/** Admin monitoring hook (ROADMAP-062). Local/demo only. */
export function AdminPage() {
  const q = useQuery({
    queryKey: ["admin"],
    queryFn: () => getJson<AdminStatus>("/api/v1/admin/status"),
  });
  const hardware = q.data?.hardware ?? {};

  return (
    <section className="vaaniq-enter space-y-8">
      <PageHeader
        title="Admin"
        subtitle="Host health, environment, and hardware snapshot for the local demo stack."
      />
      <HonestyBanner>
        Unauthenticated by design for local/capstone demos - do not expose this surface publicly.
      </HonestyBanner>
      <QueryStatus isPending={q.isPending} isError={q.isError} error={q.error ?? undefined}>
        <div className="grid gap-4 sm:grid-cols-3">
          <StatTile label="Status" value={q.data?.status ?? "-"} />
          <StatTile label="Environment" value={q.data?.env ?? "-"} />
          <StatTile label="Git SHA" value={(q.data?.git_sha ?? "-").slice(0, 10)} />
        </div>
        <Surface className="mt-6" title="Hardware">
          <table className="w-full text-left text-sm text-[var(--fg)]">
            <caption className="sr-only">Host hardware snapshot</caption>
            <tbody>
              {Object.entries(hardware).map(([key, value]) => (
                <tr key={key} className="border-t border-[var(--border)]">
                  <th className="py-3 font-medium">{key}</th>
                  <td className="py-3 text-[var(--fg-muted)]">{value}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Surface>
      </QueryStatus>
    </section>
  );
}
