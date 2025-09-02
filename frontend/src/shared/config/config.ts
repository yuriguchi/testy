export const config = {
  apiRoot: import.meta.env.VITE_APP_API_ROOT,
  apiVersion: "v2",
  repoUrl: import.meta.env.VITE_APP_REPO_URL,
  bugReportUrl: import.meta.env.VITE_APP_BUG_REPORT_URL,
  appName: "TestY",
  estimateTooltip:
    "Example formats: 120, 1d 1h 1m 1s, 2 days, 4:13:02 (uptime format), 4:13:02.266, 5hr34m56s, 5 hours, 34 minutes, 56 seconds",
  pageSizeOptions: ["10", "20", "50", "100"],
  defaultTreePageSize: 99,
  defaultLang: "en",
  debugCss: false,
}
