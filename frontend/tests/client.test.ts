import { describe, expect, it } from "vitest";

import { apiBaseUrl } from "@/api/client";
import { isLanguageCode, LANGUAGES } from "@/types/language";

describe("language types", () => {
  it("exposes exactly three project languages", () => {
    expect(LANGUAGES).toHaveLength(3);
    expect(isLanguageCode("hi")).toBe(true);
    expect(isLanguageCode("te")).toBe(false);
  });
});

describe("api client", () => {
  it("defaults API base URL when env is unset", () => {
    expect(apiBaseUrl()).toMatch(/127\.0\.0\.1:800[01]|localhost|^$/);
  });
});
