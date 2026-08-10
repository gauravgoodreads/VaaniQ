import { describe, expect, it } from "vitest";

import type { components } from "@/api/generated/schema";

describe("generated OpenAPI types", () => {
  it("exposes HealthResponse and VersionResponse schemas", () => {
    // Compile-time aliases — runtime shape check via fixture object.
    const health: components["schemas"]["HealthResponse"] = { status: "ok" };
    const version: components["schemas"]["VersionResponse"] = {
      name: "VaaniQ",
      version: "0.1.0",
      api_version: "v1",
      env: "local",
    };
    expect(health.status).toBe("ok");
    expect(version.api_version).toBe("v1");
  });
});
