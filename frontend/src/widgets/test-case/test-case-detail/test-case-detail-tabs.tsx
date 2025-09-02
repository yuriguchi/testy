import { ArrowDownOutlined } from "@ant-design/icons"
import { Button, Tabs } from "antd"
import { useMemo, useState } from "react"
import { useTranslation } from "react-i18next"

import { Toggle } from "shared/ui"

import { Comments } from "widgets/comments"

import { TestCaseHistoryChanges } from "../test-case-history-changes/test-case-history-changes"
import { TestCaseTestsList } from "../test-case-tests-list/test-case-tests-list"

type TabsEnum = "comments" | "tests" | "history"

export const TestCaseDetailTabs = ({ testCase }: { testCase: TestCase }) => {
  const { t } = useTranslation()
  const [activeTab, setActiveTab] = useState<TabsEnum>("comments")
  const [isShowArchive, setIsShowArchive] = useState(false)
  const [commentsCount, setCommentsCount] = useState(0)
  const [commentOrdering, setCommentOrdering] = useState<Ordering>("desc")

  const handleCommentOrderingClick = () => {
    setCommentOrdering(commentOrdering === "asc" ? "desc" : "asc")
  }

  const handleTabChange = (key: string) => {
    setActiveTab(key as TabsEnum)
  }

  const handleUpdateCommentsCount = (count: number) => {
    setCommentsCount(count)
  }

  const tabItems = useMemo(() => {
    return [
      {
        key: "comments",
        label: `${t("Comments")} (${commentsCount})`,
        forceRender: true,
        children: (
          <Comments
            model="testcase"
            object_id={String(testCase.id)}
            ordering={commentOrdering}
            onUpdateCommentsCount={handleUpdateCommentsCount}
          />
        ),
      },
      {
        key: "tests",
        label: t("Tests"),
        children: <TestCaseTestsList testCase={testCase} isShowArchive={isShowArchive} />,
      },
      {
        key: "history",
        label: t("History"),
        children: <TestCaseHistoryChanges testCase={testCase} />,
      },
    ]
  }, [commentsCount, commentOrdering, testCase, isShowArchive])

  const tabBarExtraContent = useMemo(() => {
    switch (activeTab) {
      case "comments":
        return (
          <Button
            type="text"
            onClick={handleCommentOrderingClick}
            data-testid="test-case-detail-comments-order-btn"
          >
            <ArrowDownOutlined style={{ rotate: commentOrdering === "asc" ? "180deg" : "0deg" }} />
          </Button>
        )

      default:
        return (
          <Toggle
            id="archive-toggle"
            label={t("Show Archived")}
            checked={isShowArchive}
            onChange={setIsShowArchive}
          />
        )
    }
  }, [activeTab, commentOrdering, isShowArchive])

  return (
    <Tabs
      defaultActiveKey="comments"
      activeKey={activeTab}
      items={tabItems}
      onChange={handleTabChange}
      tabBarExtraContent={tabBarExtraContent}
      data-testid="test-case-detail-tabs"
    />
  )
}
