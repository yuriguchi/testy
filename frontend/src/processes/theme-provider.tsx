import { ConfigProvider } from "antd"
import { ThemeConfig } from "antd/lib"
import en_US from "antd/lib/locale/en_US"
import ru_RU from "antd/lib/locale/ru_RU"
import { PropsWithChildren, useEffect, useState } from "react"
import { useTranslation } from "react-i18next"

import { getLang } from "shared/libs/local-storage"

const lightTheme: ThemeConfig = {
  token: {
    colorPrimary: "#425cd7",
    colorPrimaryHover: "#4e6bf3",
    colorInfo: "#425cd7",
    colorSuccess: "#4daf7c",
    colorWarning: "#efb622",
    colorError: "#c44d56",
    colorLink: "#425cd7",
    colorText: "#555",
    borderRadius: 4,
    fontFamily: "Proxima",
  },
  components: {
    Layout: {
      siderBg: "#222",
      triggerBg: "#222",
      bodyBg: "#f6f6f6",
      footerBg: "#f6f6f6",
    },
    Menu: {
      colorPrimary: "#555",
      itemColor: "#ffffffa6",
      itemBg: "#222",
      itemSelectedBg: "rgba(85, 85, 85, 0.22);",
      itemSelectedColor: "#fff",
      itemHoverColor: "#fff",
      itemHoverBg: "rgba(85, 85, 85, 0.22);",
    },
    Switch: {
      handleSize: 16,
      trackHeight: 24,
      trackPadding: 4,
      colorTextQuaternary: "#CBD0E2",
      colorTextTertiary: "#A8B1CE",
      trackHeightSM: 16,
      handleSizeSM: 10,
    },
    Button: {
      fontWeight: 600,
      fontSize: 12,
      lineHeight: 16,
    },
    Table: {
      borderRadius: 4,
      headerBg: "#f6f6f6",
    },
    Tag: {
      borderRadiusLG: 100,
      borderRadiusSM: 100,
      borderRadiusXS: 100,
      fontSize: 14,
      lineHeight: 16,
      fontWeightStrong: 600,
    },
    Typography: {
      fontSizeHeading1: 26,
      fontSizeHeading2: 22,
      fontSizeHeading3: 18,
      fontSizeHeading4: 16,
      fontSizeHeading5: 14,
    },
    Form: {
      verticalLabelPadding: "0 0 5px 0",
      labelColor: "#6A6E83",
    },
    Checkbox: {
      borderRadiusSM: 2,
    },
  },
}

export const ThemeProvider = ({ children }: PropsWithChildren) => {
  const { i18n } = useTranslation()
  const [locale, setLocale] = useState(getLang() === "en" ? en_US : ru_RU)

  useEffect(() => {
    if (String(locale) !== i18n.language) {
      setLocale(i18n.language === "en" ? en_US : ru_RU)
    }
  }, [i18n.language])

  return (
    <ConfigProvider theme={lightTheme} locale={locale}>
      {children}
    </ConfigProvider>
  )
}
