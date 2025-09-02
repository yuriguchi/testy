import { Divider, Flex, Typography } from "antd"
import dayjs from "dayjs"
import { TreebarContext } from "processes"
import { useContext } from "react"
import { useTranslation } from "react-i18next"
import { useParams } from "react-router-dom"

import { ArchiveTestPlan, ChangeTestPlan, CopyTestPlan, DeleteTestPlan } from "features/test-plan"

import { useTestPlanContext } from "pages/project"

import { ArchivedTag } from "shared/ui"

import {
  refetchNodeAfterArchive,
  refetchNodeAfterCreateOrCopy,
  refetchNodeAfterDelete,
} from "widgets/[ui]/treebar/utils"
import { TestsTreeContext } from "widgets/tests"

import styles from "./styles.module.css"
import { TestPlanHeaderSkeleton } from "./test-plan-header-skeleton"

export const TestPlanHeader = () => {
  const { t } = useTranslation()
  const { testPlanId } = useParams<ParamTestPlanId>()
  const { treebar } = useContext(TreebarContext)!
  const { testsTree } = useContext(TestsTreeContext)!
  const { testPlan, isFetching } = useTestPlanContext()

  const refetchParentAfterCopy = async (updatedEntity: TestPlan) => {
    const id = updatedEntity?.parent?.id ?? null
    await testsTree.current?.refetchNodeBy((node) => node.id === id && !node.props.isLeaf)
    if (!treebar.current) {
      return
    }

    await refetchNodeAfterCreateOrCopy(treebar.current, updatedEntity)
  }

  const refetchParentAfterArchive = async (updatedEntity: TestPlan) => {
    const id = updatedEntity?.parent?.id ?? null
    await testsTree.current?.refetchNodeBy((node) => node.id === id && !node.props.isLeaf)
    if (!treebar.current) {
      return
    }

    await refetchNodeAfterArchive(treebar.current, updatedEntity)
  }

  const refetchParentAfterDelete = async (updatedEntity: TestPlan) => {
    const id = updatedEntity?.parent?.id ?? null
    await testsTree.current?.refetchNodeBy((node) => node.id === id && !node.props.isLeaf)
    if (!treebar.current) {
      return
    }

    await refetchNodeAfterDelete(treebar.current, updatedEntity)
  }

  if (!testPlanId) return null

  if (!testPlan || isFetching) return <TestPlanHeaderSkeleton />

  return (
    <>
      <Flex gap={8}>
        {testPlan.is_archive && <ArchivedTag size="lg" />}
        <Typography.Title id="test-plan-title" level={2} className={styles.title}>
          {testPlan.title}
        </Typography.Title>
      </Flex>
      <Flex style={{ marginBottom: 12 }} vertical gap={16}>
        <Flex>
          {testPlan.started_at && (
            <Typography.Text
              data-testid="test-plan-detail-start-date-block"
              className={styles.infoTitle}
            >
              {t("Start date")}{" "}
              <Typography.Text className={styles.infoValue}>
                {dayjs(testPlan.started_at).format("YYYY-MM-DD")}
              </Typography.Text>
            </Typography.Text>
          )}
          {testPlan.due_date && (
            <>
              <Divider type="vertical" />
              <Typography.Text
                data-testid="test-plan-detail-due-date-block"
                className={styles.infoTitle}
              >
                {t("Due date")}{" "}
                <Typography.Text className={styles.infoValue}>
                  {dayjs(testPlan.due_date).format("YYYY-MM-DD")}
                </Typography.Text>
              </Typography.Text>
            </>
          )}
          {testPlan.finished_at && (
            <>
              <Divider type="vertical" />
              <Typography.Text
                data-testid="test-plan-detail-finish-date-block"
                className={styles.infoTitle}
              >
                {t("Finish date")}{" "}
                <Typography.Text className={styles.infoValue}>
                  {dayjs(testPlan.finished_at).format("YYYY-MM-DD")}
                </Typography.Text>
              </Typography.Text>
            </>
          )}
        </Flex>
      </Flex>
      <Flex wrap gap={8} style={{ marginBottom: 8 }}>
        <ChangeTestPlan testPlan={testPlan} type="create" />
        <CopyTestPlan testPlan={testPlan} onSubmit={refetchParentAfterCopy} />
        <ChangeTestPlan testPlan={testPlan} type="edit" />
        {!testPlan.is_archive && (
          <ArchiveTestPlan testPlan={testPlan} onSubmit={refetchParentAfterArchive} />
        )}
        <DeleteTestPlan testPlan={testPlan} onSubmit={refetchParentAfterDelete} />
      </Flex>
    </>
  )
}
