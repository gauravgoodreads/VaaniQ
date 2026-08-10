import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { App } from "@/app/App";
import { AppProviders } from "@/app/providers";
import "@/styles/globals.css";

const rootEl = document.getElementById("root");
if (!rootEl) {
  throw new Error("root element missing");
}

createRoot(rootEl).render(
  <StrictMode>
    <AppProviders>
      <App />
    </AppProviders>
  </StrictMode>,
);
