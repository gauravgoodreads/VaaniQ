import { useQuery } from "@tanstack/react-query";

import { getJson } from "@/api/client";
import { QueryStatus } from "@/components/QueryStatus";

type AdminStatus = {
  status: string;
  env: string;
  hardware: Record<string, string>;
  git_sha: string;
};

/** Admin monitoring hook (ROADMAP-062). Unauthenticated by design — local/demo only. */
export function AdminPage() {
  const q = useQuery({
    queryKey: ["admin"],
    queryFn: () => getJson<AdminStatus>("/api/v1/admin/status"),
  });
  const hardware = q.data?.hardware ?? {};
  return (
    <section className="vaaniq-enter space-y-4">
      <h1 className="font-[family-name:var(--font-display)] text-3xl">Admin</h1>
      <QueryStatus isPending={q.isPending} isError={q.isError} error={q.error ?? undefined}>
        <p className="text-sm text-[var(--fg-muted)]">
          Status {q.data?.status ?? "…"} · env {q.data?.env ?? "…"} · git {q.data?.git_sha ?? "…"}
        </p>
        <table className="w-full max-w-xl text-left text-sm">
          <caption className="sr-only">Host hardware snapshot</caption>
          <tbody>
            {Object.entries(hardware).map(([key, value]) => (
              <tr key={key} className="border-t border-[var(--border)]">
                <th className="py-1 font-medium">{key}</th>
                <td>{value}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </QueryStatus>
    </section>
  );
}
