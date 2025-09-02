import { Flex, Typography } from "antd"
import dayjs from "dayjs"
import { TreebarContext } from "processes"
import { useContext } from "react"
import { useTranslation } from "react-i18next"
import { useParams } from "react-router-dom"

import { ChangeTestSuite, CopySuite, DeleteSuite } from "features/suite"

import { useTestSuiteContext } from "pages/project"

import { refetchNodeAfterCreateOrCopy, refetchNodeAfterDelete } from "widgets/[ui]/treebar/utils"
import { TestCasesTreeContext } from "widgets/test-case"

import styles from "./styles.module.css"
import { TestSuiteHeaderSkeleton } from "./test-suite-header-skeleton"

export const TestSuiteHeader = () => {
  const { t } = useTranslation()
  const { testSuiteId } = useParams<ParamTestSuiteId>()
  const { treebar } = useContext(TreebarContext)!
  const { testCasesTree } = useContext(TestCasesTreeContext)!
  const { suite, isFetching } = useTestSuiteContext()

  const refetchParentAfterCreateOrCopy = async (updatedEntity: CopySuiteResponse) => {
    const id = updatedEntity?.parent?.id ?? null
    await testCasesTree.current?.refetchNodeBy((node) => node.id === id && !node.props.isLeaf)
    if (!treebar.current) {
      return
    }

    await refetchNodeAfterCreateOrCopy(treebar.current, updatedEntity)
  }

  const refetchParentAfterDelete = async (updatedEntity: Suite) => {
    const id = updatedEntity?.parent?.id ?? null
    await testCasesTree.current?.refetchNodeBy((node) => node.id === id && !node.props.isLeaf)
    if (!treebar.current) {
      return
    }

    await refetchNodeAfterDelete(treebar.current, updatedEntity)
  }

  if (!testSuiteId) return null

  if (!suite || isFetching) return <TestSuiteHeaderSkeleton />

  return (
    <>
      <Flex gap={8}>
        <Typography.Title id="test-suite-title" level={2} className={styles.title}>
          {suite.name}
        </Typography.Title>
      </Flex>
      <Flex style={{ marginBottom: 12 }} vertical gap={16}>
        <Flex>
          {suite.created_at && (
            <Typography.Text className={styles.infoTitle}>
              {t("Created At")}{" "}
              <Typography.Text className={styles.infoValue}>
                {dayjs(suite.created_at).format("YYYY-MM-DD")}
              </Typography.Text>
            </Typography.Text>
          )}
        </Flex>
      </Flex>
      <Flex wrap gap={8} style={{ marginBottom: 8 }}>
        <ChangeTestSuite suite={suite} type="create" />
        <CopySuite suite={suite} onSubmit={refetchParentAfterCreateOrCopy} />
        <ChangeTestSuite suite={suite} type="edit" />
        <DeleteSuite suite={suite} onSubmit={refetchParentAfterDelete} />
      </Flex>
    </>
  )
}
