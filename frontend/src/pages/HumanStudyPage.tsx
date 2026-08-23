import { useMutation, useQuery } from "@tanstack/react-query";
import { useRef, useState } from "react";

import { apiBaseUrl } from "@/api/client";
import { Button } from "@/components/ui/button";

type Participant = {
  participant_id: string;
  fluency_self_report: string;
  clip_ids: string[];
};

type Report = {
  n_responses: number;
  stats: Record<string, unknown>;
};

/** Human listening-test UI (RQ5 / O6 / ROADMAP-059). */
export function HumanStudyPage() {
  const [fluency, setFluency] = useState("hi+mr");
  const [choice, setChoice] = useState("real");
  const [confidence, setConfidence] = useState(3);
  const [index, setIndex] = useState(0);
  const started = useRef(0);
  const register = useMutation({
    mutationFn: async () => {
      const res = await fetch(`${apiBaseUrl()}/api/v1/human-study/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fluency_self_report: fluency }),
      });
      if (!res.ok) throw new Error("register failed");
      started.current = Date.now();
      setIndex(0);
      return (await res.json()) as Participant;
    },
  });
  const report = useQuery({
    queryKey: ["human-report"],
    queryFn: async () => {
      const res = await fetch(`${apiBaseUrl()}/api/v1/human-study/report`);
      if (!res.ok) throw new Error("report failed");
      return (await res.json()) as Report;
    },
  });
  const session = register.data;
  const clipId = session?.clip_ids[index] ?? "";

  async function submitTrial() {
    if (!session) return;
    const body = {
      participant_id: session.participant_id,
      clip_id: clipId,
      choice,
      confidence_1_5: confidence,
      response_ms: Date.now() - started.current,
      language: clipId.split("-")[0] ?? "hi",
      compression_status: "clean",
    };
    const res = await fetch(`${apiBaseUrl()}/api/v1/human-study/response`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error("response failed");
    started.current = Date.now();
    setIndex((i) => Math.min(i + 1, (session.clip_ids.length || 1) - 1));
    await report.refetch();
  }

  return (
    <section className="vaaniq-enter space-y-4">
      <h1 className="font-[family-name:var(--font-display)] text-3xl">Human study</h1>
      <p className="max-w-2xl text-[var(--fg-muted)]">
        Anonymous volunteer protocol (OQ-011): 36 clips, 1–5 confidence, real/fake, timed.
        Audio playback requires ingested object-store files.
      </p>
      <label className="grid max-w-sm gap-1 text-sm">
        Fluency self-report
        <input
          className="rounded border border-[var(--border)] bg-transparent px-2 py-1"
          value={fluency}
          onChange={(e) => setFluency(e.target.value)}
          aria-label="Fluency self-report"
        />
      </label>
      <Button type="button" onClick={() => register.mutate()} disabled={register.isPending}>
        Register anonymous ID
      </Button>
      {session ? (
        <div className="space-y-3 rounded-lg border border-[var(--border)] p-4">
          <p className="text-sm">
            Participant <code>{session.participant_id}</code> · clip {index + 1}/
            {session.clip_ids.length}: <code>{clipId}</code>
          </p>
          <fieldset className="flex gap-4 text-sm">
            <legend className="sr-only">Real or fake</legend>
            <label>
              <input
                type="radio"
                name="choice"
                value="real"
                checked={choice === "real"}
                onChange={() => setChoice("real")}
              />{" "}
              Real
            </label>
            <label>
              <input
                type="radio"
                name="choice"
                value="fake"
                checked={choice === "fake"}
                onChange={() => setChoice("fake")}
              />{" "}
              Fake
            </label>
          </fieldset>
          <label className="grid max-w-sm gap-1 text-sm">
            Confidence (1–5)
            <input
              type="range"
              min={1}
              max={5}
              value={confidence}
              aria-label="Confidence slider"
              onChange={(e) => setConfidence(Number(e.target.value))}
            />
            <span>{confidence}</span>
          </label>
          <Button type="button" onClick={() => void submitTrial()}>
            Submit trial
          </Button>
        </div>
      ) : null}
      <div>
        <h2 className="text-lg">Human vs model</h2>
        <p className="text-sm text-[var(--fg-muted)]">N={report.data?.n_responses ?? 0}</p>
        <pre className="overflow-auto rounded border border-[var(--border)] p-3 text-xs">
          {JSON.stringify(report.data?.stats ?? {}, null, 2)}
        </pre>
      </div>
    </section>
  );
}
