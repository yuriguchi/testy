import { useTranslation } from "react-i18next"

import { config } from "shared/config"

import packageJson from "../../../../package.json"

export const Copyright = () => {
  const { t } = useTranslation()

  return (
    <p style={{ textAlign: "center", marginBottom: 0, fontSize: 12 }}>
      <a target="_blank" href={config.repoUrl} rel="noreferrer">
        TestY TMS {t("version")} {packageJson.version}
      </a>
      . {t("Released under the AGPL-v3 License")}.
      <br />
      {t("Found a bug or have a comment?")}&nbsp; {t("Please report an")}{" "}
      <a target="_blank" rel="noreferrer" href={config.bugReportUrl}>
        {t("issue")}
      </a>{" "}
      {t("or")} <a href="mailto:testy@yadro.com">{t("email us")}</a> .
      <br />
      {t("Copyright")} © {new Date().getFullYear()}{" "}
      <a target="_blank" href="https://yadro.com" rel="noreferrer">
        KNS Group LLC (YADRO).
      </a>
    </p>
  )
}
