// sort-imports-ignore
import i18n from "i18next"
import { ThemeProvider } from "processes"
import { createRoot } from "react-dom/client"
import { initReactI18next } from "react-i18next"
import { Provider } from "react-redux"
import { PersistGate } from "redux-persist/integration/react"

import "shared/assets/fonts/proxima-nova-semibold.ttf"
import "shared/assets/fonts/proxima.ttf"
import { i18nConfig } from "shared/config/i18n-config"
import { getLang } from "shared/libs/local-storage"

import App from "./App"
import { persistor, store } from "./app/store"

i18n.use(initReactI18next).init({
  resources: i18nConfig,
  lng: getLang(),
  fallbackLng: getLang(),
  interpolation: {
    escapeValue: false,
  },
})

// eslint-disable-next-line @typescript-eslint/no-non-null-assertion
const container = document.getElementById("root")!
const root = createRoot(container)

root.render(
  <Provider store={store}>
    <PersistGate loading={null} persistor={persistor}>
      <ThemeProvider>
        <App />
      </ThemeProvider>
    </PersistGate>
  </Provider>
)
