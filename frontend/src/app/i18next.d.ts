import { i18nConfig } from "shared/config/i18n-config"

declare module "i18next" {
  interface CustomTypeOptions {
    resources: (typeof i18nConfig)["en"]
  }
}
