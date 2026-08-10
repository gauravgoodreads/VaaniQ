/** Hand-written until OpenAPI types land (Phase 1 step 11 / ROADMAP-007). */
export type HealthResponse = {
  status: string;
};

export type VersionResponse = {
  name: string;
  version: string;
  api_version: string;
  env: string;
};
