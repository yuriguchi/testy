import { useTranslation } from "react-i18next"

import styles from "./styles.module.css"

interface Props {
  descendant_count: number | null
  total_cases_count: number | null
  cases_count: number | null
  estimate: string | null
}

export const TestSuitePopoverInfo = ({
  descendant_count,
  total_cases_count,
  cases_count,
  estimate,
}: Props) => {
  const { t } = useTranslation()
  return (
    <ul className={styles.ul}>
      <li>
        {t("Test Suites")} <span className={styles.value}>{descendant_count ?? 0}</span>
      </li>
      <li>
        {t("Test Cases")}{" "}
        <span className={styles.value}>
          {cases_count ?? 0} ({total_cases_count ?? 0})
        </span>
      </li>
      <li>
        {t("Estimate")} <span className={styles.value}>{estimate ?? "-"}</span>
      </li>
    </ul>
  )
}
