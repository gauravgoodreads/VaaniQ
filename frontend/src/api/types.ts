/**
 * API type aliases sourced from OpenAPI-generated ``schema.ts``.
 *
 * Hand-written response models are forbidden — regenerate with
 * ``scripts/gen_api_types.sh`` / ``npm run gen:api-types``.
 */
import type { components } from "@/api/generated/schema";

export type HealthResponse = components["schemas"]["HealthResponse"];
export type ReadyResponse = components["schemas"]["ReadyResponse"];
export type VersionResponse = components["schemas"]["VersionResponse"];

export type { components, operations, paths } from "@/api/generated/schema";
