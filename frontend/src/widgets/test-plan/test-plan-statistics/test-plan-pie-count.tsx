import { Flex, Spin } from "antd"
import { useTranslation } from "react-i18next"
import { useParams } from "react-router-dom"

import { useAppDispatch, useAppSelector } from "app/hooks"

import { selectFilter, updateFilter } from "entities/test/model"

import { useGetTestPlanStatisticsQuery } from "entities/test-plan/api"

import { Pie } from "shared/ui"

import styles from "./styles.module.css"

interface Props {
  testPlanId?: number
  height: number
  onHeightChange: (height: number) => void
}

export const TestPlanPieCount = ({ testPlanId, height, onHeightChange }: Props) => {
  const { t } = useTranslation()
  const { projectId } = useParams<ParamProjectId>()
  const testsFilter = useAppSelector(selectFilter)
  const dispatch = useAppDispatch()

  const { data: pieData, isFetching } = useGetTestPlanStatisticsQuery(
    {
      parent: testPlanId ? Number(testPlanId) : null,
      labels: testsFilter.labels?.length ? testsFilter.labels : undefined,
      not_labels: testsFilter.not_labels?.length ? testsFilter.not_labels : undefined,
      labels_condition: testsFilter.labels_condition ?? undefined,
      is_archive: testsFilter.is_archive,
      project: Number(projectId),
    },
    { skip: !projectId }
  )

  const handleStatusesUpdate = (statuses: string[]) => {
    dispatch(updateFilter({ statuses }))
  }

  return (
    <div className={styles.pieWrapper}>
      <h3 className={styles.graphsTitle}>{t("Tests Count")}</h3>
      {isFetching && (
        <Flex align="center" justify="center" style={{ height: "100%" }}>
          <Spin size="large" />
        </Flex>
      )}
      {!isFetching && (
        <Pie
          statuses={testsFilter.statuses}
          updateStatuses={handleStatusesUpdate}
          data={pieData ?? []}
          type="value"
          height={height}
          onHeightChange={onHeightChange}
        />
      )}
    </div>
  )
}
