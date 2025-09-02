import translationRU from "shared/locales/ru.json"

const genByKeys = <T extends Record<string, string>>(ruData: T): T => {
  const en = {}
  Object.keys(ruData).forEach((key) => {
    // @ts-ignore
    en[key] = key
  })
  // @ts-ignore
  return en
}

export const i18nConfig = {
  en: {
    translation: genByKeys(translationRU),
  },
  ru: {
    translation: translationRU,
  },
}
