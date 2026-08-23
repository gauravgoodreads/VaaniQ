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
export type PredictionResponse = components["schemas"]["PredictionResponse"];
export type UploadResponse = components["schemas"]["UploadResponse"];
export type HistoryResponse = components["schemas"]["HistoryResponse"];
export type ExperimentsResponse = components["schemas"]["ExperimentsResponse"];
export type MetricsResponse = components["schemas"]["MetricsResponse"];
export type CalibrationResponse = components["schemas"]["CalibrationResponse"];
export type ExplainResponse = components["schemas"]["ExplainResponse"];
export type ReportResponse = components["schemas"]["ReportResponse"];
export type AdminStatusResponse = components["schemas"]["AdminStatusResponse"];
export type DatasetExplorerResponse = components["schemas"]["DatasetExplorerResponse"];
export type ExperimentCompareResponse = components["schemas"]["ExperimentCompareResponse"];
export type HumanStudyReportResponse = components["schemas"]["HumanStudyReportResponse"];
export type ParticipantResponse = components["schemas"]["ParticipantResponse"];

export type { components, operations, paths } from "@/api/generated/schema";
