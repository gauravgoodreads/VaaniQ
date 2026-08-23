import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";

import { AppRouter } from "@/app/router";
import { LANGUAGES } from "@/types/language";

function renderApp(initialPath = "/") {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[initialPath]}>
        <AppRouter />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("frontend shell", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        Promise.resolve({
          ok: true,
          json: async () => ({ status: "ok" }),
        }),
      ),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders VaaniQ brand and languages without Telugu", async () => {
    renderApp("/");
    expect(screen.getAllByText("VaaniQ").length).toBeGreaterThan(0);
    expect(LANGUAGES).toEqual(["hi", "mr", "ta"]);
    expect(LANGUAGES).not.toContain("te");
    await waitFor(() => {
      expect(screen.getByTestId("landing-health")).toHaveTextContent(/Connected/);
    });
  });

  it("calls /health via the API client", async () => {
    renderApp("/");
    await waitFor(() => {
      expect(fetch).toHaveBeenCalled();
    });
    const calls = vi.mocked(fetch).mock.calls;
    const healthCall = calls.find((call) => String(call[0]).includes("/health"));
    expect(healthCall).toBeDefined();
  });

  it("routes to upload page with detect action", async () => {
    renderApp("/upload");
    expect(await screen.findByRole("heading", { name: "Upload" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Detect" })).toBeInTheDocument();
  });

  it("renders human study registration", async () => {
    renderApp("/human-study");
    expect(await screen.findByRole("heading", { name: "Human study" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Register anonymous ID" })).toBeInTheDocument();
  });

  it("exposes a skip-to-content link", () => {
    renderApp("/");
    expect(screen.getByRole("link", { name: "Skip to content" })).toHaveAttribute(
      "href",
      "#main-content",
    );
  });

  it.each([
    ["/", "VaaniQ"],
    ["/dashboard", "Dashboard"],
    ["/upload", "Upload"],
    ["/live", "Live"],
    ["/inference", "Inference"],
    ["/history", "History"],
    ["/research-metrics", "Research metrics"],
    ["/experiments", "Experiments"],
    ["/calibration", "Calibration"],
    ["/explainability", "Explainability"],
    ["/human-study", "Human study"],
    ["/datasets", "Dataset explorer"],
    ["/admin", "Admin"],
    ["/docs", "Docs"],
  ] as const)("renders %s heading", async (path, heading) => {
    renderApp(path);
    expect(await screen.findByRole("heading", { name: heading })).toBeInTheDocument();
  });
});
