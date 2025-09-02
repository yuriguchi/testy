import { Divider, Flex } from "antd"
import { useTranslation } from "react-i18next"
import { TestPlanDataActions, TestPlanStatistics } from "widgets"

import { useCacheState } from "shared/hooks"
import { Collapse, Markdown } from "shared/ui"

import { TestDetail, TestsTable, TestsTree } from "widgets/tests"

import { useTestPlanContext } from "../test-plan-layout/test-plan-layout"
import styles from "./styles.module.css"

type EntityView = "list" | "tree"

export const TestPlansOverviewTab = () => {
  const { t } = useTranslation()
  const [dataView, setDataView] = useCacheState<EntityView>("test-plan-detail-tests-view", "tree")
  const { testPlan, hasTestPlan } = useTestPlanContext()

  return (
    <Flex vertical style={{ width: "100%" }}>
      {hasTestPlan && testPlan?.description && (
        <>
          <Collapse
            cacheKey="test-plan-description"
            defaultCollapse={false}
            title={<span className={styles.collapseTitle}>{t("Description")}</span>}
            data-testid="test-plan-description-collapse"
          >
            <div data-testid="test-plan-description">
              <Markdown content={testPlan.description} />
            </div>
          </Collapse>
          <Divider />
        </>
      )}
      <Collapse
        cacheKey="test-plan-statistic"
        defaultCollapse
        title={
          <span data-testid="test-plan-statistic-title" className={styles.collapseTitle}>
            {t("Statistic")}
          </span>
        }
      >
        <TestPlanStatistics testPlanId={testPlan?.id} />
      </Collapse>
      <Divider />
      <TestPlanDataActions
        testPlanId={testPlan?.id}
        dataView={dataView}
        setDataView={setDataView}
      />
      {dataView === "list" && <TestsTable testPlanId={testPlan?.id} />}
      {dataView === "tree" && <TestsTree testPlanId={testPlan?.id} />}
      <TestDetail />
    </Flex>
  )
}
