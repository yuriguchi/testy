import { ArrowDownOutlined } from "@ant-design/icons"
import { Button, Flex, Tabs, Typography } from "antd"
import { useContext, useEffect, useMemo, useState } from "react"
import { useTranslation } from "react-i18next"
import { Link, useParams } from "react-router-dom"
import { Comments } from "widgets"

import { ResultList } from "entities/result/ui"

import { useTestDetail } from "entities/test/model"

import { TestCaseFields } from "entities/test-case/ui/test-case-fields"

import { AddResult, AssignTo } from "features/test-result"

import { ProjectContext } from "pages/project"

import { ArchivedTag, Drawer, Toggle } from "shared/ui"

import { TestsTreeContext } from "../tests-tree"
import styles from "./styles.module.css"

export const TestDetail = () => {
  const { t } = useTranslation()
  const { project } = useContext(ProjectContext)!
  const { testsTree } = useContext(TestsTreeContext)!
  const { testPlanId } = useParams<ParamTestPlanId>()

  const {
    drawerTest,
    testCase,
    isFetching,
    showArchive,
    commentOrdering,
    tab,
    handleShowArchived,
    handleCloseDetails,
    handleCommentOrderingClick,
    handleTabChange,
  } = useTestDetail()
  const [commentsCount, setCommentsCount] = useState(0)

  const isLoadingDrawer = isFetching || !project || !drawerTest

  useEffect(() => {
    if (!isLoadingDrawer && location.hash && location.hash.includes("comment")) {
      handleTabChange("comments")
    }
  }, [location, isLoadingDrawer])

  const handleRefetch = async () => {
    if (String(drawerTest?.plan) === String(testPlanId)) {
      await testsTree.current?.initRoot({ initParent: testPlanId })
      return
    }

    await testsTree.current?.refetchNodeBy((node) => node.id === drawerTest?.plan)
  }

  const tabItems = useMemo(() => {
    if (!drawerTest || !testCase) {
      return []
    }

    return [
      {
        label: t("Results"),
        key: "results",
        children: (
          <ResultList
            testId={drawerTest.id}
            testCase={testCase}
            isProjectArchive={project.is_archive}
          />
        ),
      },
      {
        label: `${t("Comments")} (${commentsCount})`,
        key: "comments",
        forceRender: true,
        children: (
          <Comments
            model="test"
            object_id={String(drawerTest.id)}
            ordering={commentOrdering}
            onUpdateCommentsCount={setCommentsCount}
          />
        ),
      },
    ]
  }, [commentOrdering, drawerTest, testCase, commentsCount])

  const tabBarExtraContent = useMemo(() => {
    if (tab === "comments") {
      return (
        <Button type="text" onClick={handleCommentOrderingClick}>
          <ArrowDownOutlined style={{ rotate: commentOrdering === "asc" ? "180deg" : "0deg" }} />
        </Button>
      )
    }

    return (
      <Toggle
        id="result-show-archived-toggle"
        checked={showArchive}
        onChange={handleShowArchived}
        label={t("Show Archived")}
      />
    )
  }, [tab, commentOrdering, showArchive, handleShowArchived])

  return (
    <Drawer
      id="drawer-test-detail"
      isOpen={!!drawerTest}
      isLoading={isLoadingDrawer}
      onClose={handleCloseDetails}
      minWidth={400}
      extra={
        testCase && (
          <AddResult isDisabled={project.is_archive} testCase={testCase} onSubmit={handleRefetch} />
        )
      }
      title={
        testCase &&
        drawerTest && (
          <Flex align="flex-start" style={{ width: "fit-content", marginRight: "auto" }}>
            <Flex vertical>
              <Flex gap={8}>
                {drawerTest.is_archive && (
                  <Flex
                    justify="center"
                    align="center"
                    style={{ height: 32 }}
                    data-testid="test-detail-archive-tag"
                  >
                    <ArchivedTag />
                  </Flex>
                )}
                <Typography.Title
                  level={3}
                  className={styles.title}
                  data-testid="test-detail-title"
                >
                  {drawerTest.name}
                </Typography.Title>
              </Flex>
              <Link
                style={{ color: "var(--y-grey-30)", fontSize: 14, textDecoration: "underline" }}
                to={`/projects/${drawerTest.project}/suites/${testCase.suite.id}/?test_case=${testCase.id}&version=${testCase.current_version}`}
                data-testid="test-detail-version"
              >
                {t("Actual ver.")} {testCase.current_version}
              </Link>
            </Flex>
          </Flex>
        )
      }
    >
      {testCase && drawerTest && (
        <>
          <TestCaseFields testCase={testCase} />
          <AssignTo onSuccess={handleRefetch} />
          <Tabs
            defaultActiveKey="results"
            activeKey={tab}
            onChange={handleTabChange}
            tabBarExtraContent={tabBarExtraContent}
            items={tabItems}
          />
        </>
      )}
    </Drawer>
  )
}
