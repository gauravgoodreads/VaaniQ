import { Route, Routes } from "react-router-dom";

import { AppShell } from "@/components/layout/AppShell";
import { AdminPage } from "@/pages/AdminPage";
import { CalibrationPage } from "@/pages/CalibrationPage";
import { DashboardPage } from "@/pages/DashboardPage";
import { DocsPage } from "@/pages/DocsPage";
import { ExperimentsPage } from "@/pages/ExperimentsPage";
import { ExplainabilityPage } from "@/pages/ExplainabilityPage";
import { HistoryPage } from "@/pages/HistoryPage";
import { InferencePage } from "@/pages/InferencePage";
import { LandingPage } from "@/pages/LandingPage";
import { LivePage } from "@/pages/LivePage";
import { ResearchMetricsPage } from "@/pages/ResearchMetricsPage";
import { UploadPage } from "@/pages/UploadPage";

/** Application route table (12 pages + shell). */
export function AppRouter() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<LandingPage />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="upload" element={<UploadPage />} />
        <Route path="live" element={<LivePage />} />
        <Route path="inference" element={<InferencePage />} />
        <Route path="history" element={<HistoryPage />} />
        <Route path="research-metrics" element={<ResearchMetricsPage />} />
        <Route path="experiments" element={<ExperimentsPage />} />
        <Route path="calibration" element={<CalibrationPage />} />
        <Route path="explainability" element={<ExplainabilityPage />} />
        <Route path="admin" element={<AdminPage />} />
        <Route path="docs" element={<DocsPage />} />
      </Route>
    </Routes>
  );
}
