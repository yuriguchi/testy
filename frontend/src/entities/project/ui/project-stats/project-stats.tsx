import { useTranslation } from "react-i18next"

import styles from "./styles.module.css"

interface Props {
  testSuites: number
  testCases: number
  testPlans: number
  tests: number
}

export const ProjectStats = ({
  testSuites = 0,
  testCases = 0,
  testPlans = 0,
  tests = 0,
}: Props) => {
  const { t } = useTranslation()

  return (
    <ul className={styles.wrapper} data-testid="project-stats">
      <li
        className={styles.card}
        style={{ borderColor: "var(--y-graph-primary)" }}
        data-testid="project-stats-test-suites"
      >
        <span className={styles.cardValue}>{testSuites}</span>
        <span>{t("Test Suites")}</span>
      </li>
      <li
        className={styles.card}
        style={{ borderColor: "var(--y-graph-secondary)" }}
        data-testid="project-stats-test-cases"
      >
        <span className={styles.cardValue}>{testCases}</span>
        <span>{t("Test Cases")}</span>
      </li>
      <li
        className={styles.card}
        style={{ borderColor: "var(--y-graph-fourth)" }}
        data-testid="project-stats-test-plans"
      >
        <span className={styles.cardValue}>{testPlans}</span>
        <span>{t("Test Plans")}</span>
      </li>
      <li
        className={styles.card}
        style={{ borderColor: "var(--y-graph-fifth)" }}
        data-testid="project-stats-tests"
      >
        <span className={styles.cardValue}>{tests}</span>
        <span>{t("Tests")}</span>
      </li>
    </ul>
  )
}
