import { Link } from "react-router-dom";
import { useEffect, useRef } from "react";

import { useHealth } from "@/hooks/useHealth";
import { LANGUAGES } from "@/types/language";

/** Animated waveform plane - product-relevant visual for the hero. */
function HeroWavefield() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let raf = 0;
    let running = true;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = canvas.clientWidth * dpr;
      canvas.height = canvas.clientHeight * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    resize();
    window.addEventListener("resize", resize);

    const draw = (t: number) => {
      const w = canvas.clientWidth;
      const h = canvas.clientHeight;
      ctx.clearRect(0, 0, w, h);

      const rows = 7;
      for (let r = 0; r < rows; r += 1) {
        const y = (h / (rows + 1)) * (r + 1);
        ctx.beginPath();
        for (let x = 0; x <= w; x += 4) {
          const phase = reduce ? r * 0.7 : t * 0.0012 + r * 0.85;
          const amp = 10 + r * 4;
          const yOff =
            Math.sin(x * 0.012 + phase) * amp +
            Math.sin(x * 0.031 - phase * 1.3) * (amp * 0.35);
          if (x === 0) ctx.moveTo(x, y + yOff);
          else ctx.lineTo(x, y + yOff);
        }
        ctx.strokeStyle = `color-mix(in oklab, #7dffd4 ${18 + r * 8}%, transparent)`;
        ctx.lineWidth = 1.4;
        ctx.stroke();
      }
      if (!reduce) raf = requestAnimationFrame(draw);
    };

    raf = requestAnimationFrame(draw);
    return () => {
      running = false;
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
      void running;
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 h-full w-full"
      aria-hidden
    />
  );
}

/** Marketing/home surface - brand-first full-bleed hero with live API health. */
export function LandingPage() {
  const health = useHealth();

  return (
    <div className="-mx-4 -mt-8 md:-mx-4">
      <section className="relative isolate min-h-[calc(100vh-5.5rem)] overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_90%_70%_at_70%_20%,#163a38_0%,#071216_55%,#04090c_100%)]" />
        <div className="absolute inset-0 opacity-70">
          <HeroWavefield />
        </div>
        <div
          className="absolute inset-0 opacity-[0.12]"
          style={{
            backgroundImage:
              "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")",
          }}
          aria-hidden
        />

        <div className="relative z-10 mx-auto flex min-h-[calc(100vh-5.5rem)] max-w-6xl flex-col justify-end px-4 pb-16 pt-24 text-[#e8f2f0] md:pb-20">
          <div className="vaaniq-hero-rise max-w-3xl space-y-6">
            <h1 className="font-[family-name:var(--font-display)] text-6xl leading-[0.95] tracking-tight md:text-8xl">
              VaaniQ
            </h1>
            <p className="max-w-xl text-lg text-white/70 md:text-xl">
              Hear what is human. Calibrated detection of AI-generated voice across Hindi,
              Marathi, and Tamil - built for compression-rough, real-world audio.
            </p>
            <div className="flex flex-wrap items-center gap-3 pt-2">
              <Link
                to="/upload"
                className="inline-flex h-12 items-center rounded-full bg-[#7dffd4] px-7 text-sm font-semibold text-[#04120f] transition hover:brightness-110"
              >
                Record or upload
              </Link>
              <Link
                to="/live"
                className="inline-flex h-12 items-center rounded-full border border-white/25 px-7 text-sm text-white/90 transition hover:bg-white/10"
              >
                Open live mic
              </Link>
            </div>
            <p
              className="pt-4 text-sm text-white/50"
              data-testid="landing-health"
            >
              {health.isPending && "Checking API…"}
              {health.isSuccess && `Connected · ${LANGUAGES.join(" · ").toUpperCase()}`}
              {health.isError && "API offline - start the backend on :8000"}
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
