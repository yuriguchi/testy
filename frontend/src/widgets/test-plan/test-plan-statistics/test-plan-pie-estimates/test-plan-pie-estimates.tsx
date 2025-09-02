import { Flex, Spin } from "antd"
import { MeContext } from "processes"
import { useContext, useEffect, useMemo, useState } from "react"
import { useTranslation } from "react-i18next"
import { useParams } from "react-router-dom"
import { Label, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts"

import { useAppDispatch, useAppSelector } from "app/hooks"

import { selectFilter, updateFilter } from "entities/test/model"

import { useGetTestPlanStatisticsQuery } from "entities/test-plan/api"

import { PieCellList } from "shared/ui"
import { usePie } from "shared/ui/pie/model/use-pie"

import styles from "../styles.module.css"
import { TestPlanPieEstimatesFilters } from "./test-plan-pie-estimates-filters"

interface Props {
  testPlanId?: number
  height: number
  onHeightChange: (height: number) => void
}

const DEFAULT_ESTIMATE: EstimatePeriod = "minutes"

export const TestPlanPieEstimates = ({ testPlanId, height, onHeightChange }: Props) => {
  const { t } = useTranslation()
  const { projectId } = useParams<ParamProjectId>()
  const testsFilter = useAppSelector(selectFilter)
  const dispatch = useAppDispatch()

  const { userConfig, updateConfig } = useContext(MeContext)
  const [period, setPeriod] = useState<EstimatePeriod>(
    userConfig?.ui?.test_plan_estimate_everywhere_period ?? DEFAULT_ESTIMATE
  )

  const { data: pieData, isFetching } = useGetTestPlanStatisticsQuery(
    {
      parent: testPlanId ? Number(testPlanId) : null,
      labels: testsFilter.labels?.length ? testsFilter.labels : undefined,
      not_labels: testsFilter.not_labels?.length ? testsFilter.not_labels : undefined,
      labels_condition: testsFilter.labels_condition ?? undefined,
      is_archive: testsFilter.is_archive,
      project: Number(projectId),
      estimate_period: period,
    },
    { skip: !projectId }
  )

  const handleStatusesUpdate = (statuses: string[]) => {
    dispatch(updateFilter({ statuses }))
  }

  const {
    formatData,
    total,
    legendFormatter,
    tooltipFormatter,
    handleCellClick,
    checkActive,
    chartRef,
  } = usePie({
    data: pieData ?? [],
    type: "estimates",
    period,
    statuses: testsFilter.statuses,
    updateStatuses: handleStatusesUpdate,
    onHeightChange,
  })

  const estimatesStats = useMemo(() => {
    const empty = (pieData ?? []).reduce(
      (acc, item) => (item.label === "UNTESTED" ? acc : acc + item.empty_estimates),
      0
    ) // left number
    const newTotal = (pieData ?? []).reduce((acc, item) => acc + item.empty_estimates, 0) // right number
    return {
      empty,
      total: newTotal,
    }
  }, [formatData])

  const handlePeriodChange = async (newPeriod: EstimatePeriod) => {
    setPeriod(newPeriod)
    await updateConfig({
      ...userConfig,
      ui: {
        ...userConfig?.ui,
        test_plan_estimate_everywhere_period: newPeriod,
      },
    })
  }

  useEffect(() => {
    setPeriod(userConfig?.ui?.test_plan_estimate_everywhere_period ?? DEFAULT_ESTIMATE)
  }, [testPlanId])

  return (
    <div className={styles.pieWrapper}>
      <div className={styles.pieHeader}>
        <h3 className={styles.graphsTitle}>{t("Tests Estimates")}</h3>
        <TestPlanPieEstimatesFilters setPeriod={handlePeriodChange} value={period} />
      </div>
      {isFetching && (
        <Flex align="center" justify="center" style={{ height: "100%" }}>
          <Spin size="large" />
        </Flex>
      )}
      {!isFetching && (
        <>
          <ResponsiveContainer width="100%" height={height} ref={chartRef}>
            <PieChart margin={{ left: 0 }}>
              <Pie
                data={formatData}
                dataKey="estimates"
                nameKey="label"
                cx="50%"
                cy="50%"
                innerRadius={80}
                outerRadius={94}
                fill="#a0a0a0"
              >
                <PieCellList
                  data={formatData}
                  checkActive={checkActive}
                  handleCellClick={handleCellClick}
                />
                <Label position="centerBottom" fontSize={26} value={t("Total")} />
                <Label
                  value={parseFloat(total.toFixed(2))}
                  position="centerTop"
                  offset={20}
                  fontSize={28}
                  style={{ marginTop: 20 }}
                  dy={12}
                  fill="#000"
                  fontWeight="bold"
                />
              </Pie>
              <Legend
                iconSize={10}
                layout="vertical"
                verticalAlign="middle"
                align="right"
                iconType="circle"
                formatter={legendFormatter}
              />
              <Tooltip formatter={tooltipFormatter} />
            </PieChart>
          </ResponsiveContainer>
          <div
            className={styles.notEstimatedBlock}
            data-testid="test-plan-pie-estimates-not-estimated-block"
          >
            <span>
              {t("Not estimated tests statistics")}:{" "}
              {`${estimatesStats.empty}/${estimatesStats.total}`}
            </span>
          </div>
        </>
      )}
    </div>
  )
}
