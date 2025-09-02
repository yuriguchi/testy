import { Divider, Flex } from "antd"
import { useTranslation } from "react-i18next"
import { TestSuiteDataActions } from "widgets"

import { useCacheState } from "shared/hooks"
import { Collapse, Markdown } from "shared/ui"

import { TestCaseDetail, TestCasesTable, TestsCasesTree } from "widgets/test-case"

import { useTestSuiteContext } from "../test-suite-layout"
import styles from "./styles.module.css"

type EntityView = "list" | "tree"

export const TestSuitesOverviewTab = () => {
  const { t } = useTranslation()
  const [dataView, setDataView] = useCacheState<EntityView>(
    "test-suite-detail-test-cases-view",
    "tree"
  )
  const { suite, hasTestSuite } = useTestSuiteContext()

  return (
    <Flex vertical style={{ width: "100%" }}>
      {hasTestSuite && suite?.description && (
        <>
          <Collapse
            cacheKey="test-suite-description"
            defaultCollapse={false}
            title={<span className={styles.collapseTitle}>{t("Description")}</span>}
            data-testid="test-suite-description-collapse"
          >
            <div data-testid="test-suite-description">
              <Markdown content={suite.description} />
            </div>
          </Collapse>
          <Divider />
        </>
      )}
      <TestSuiteDataActions dataView={dataView} setDataView={setDataView} suite={suite} />
      {dataView === "list" && <TestCasesTable />}
      {dataView === "tree" && <TestsCasesTree />}
      <TestCaseDetail />
    </Flex>
  )
}
