import { FetchBaseQueryError, QueryActionCreatorResult } from "@reduxjs/toolkit/query"
import { QueryDefinition } from "@reduxjs/toolkit/query"
import { BaseQueryFn } from "@reduxjs/toolkit/query"
import { FetchArgs } from "@reduxjs/toolkit/query"
import { Tabs, TabsProps } from "antd"
import { MeContext } from "processes"
import React, { useContext, useEffect, useState } from "react"
import { useTranslation } from "react-i18next"
import { Outlet, useLocation, useNavigate, useParams } from "react-router-dom"
import { TestPlanHeader } from "widgets"

import { useGetTestPlanQuery } from "entities/test-plan/api"

import { TestsTreeProvider } from "widgets/tests"

import { useProjectContext } from "../../project-layout"

export interface TestPlanContextType {
  testPlan?: TestPlan
  isFetching: boolean
  refetch: () => QueryActionCreatorResult<
    QueryDefinition<
      TestPlanQuery,
      BaseQueryFn<string | FetchArgs, unknown, FetchBaseQueryError>,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      any,
      TestPlan,
      "testPlanApi"
    >
  >
  hasTestPlan: boolean
}

export const TestPlanContext = React.createContext<TestPlanContextType | null>(null)

type TestPlanTabs = "overview" | "activity" | "custom-attributes" | "attachments"
const tabKeys = ["overview", "activity", "custom-attributes", "attachments"]

export const TestPlanLayout = () => {
  const { t } = useTranslation()
  const project = useProjectContext()
  const { testPlanId } = useParams<ParamTestPlanId>()
  const { userConfig } = useContext(MeContext)
  const navigate = useNavigate()
  const location = useLocation()
  const [tab, setTab] = useState<TestPlanTabs>("overview")

  const {
    data: testPlan,
    isFetching,
    refetch,
  } = useGetTestPlanQuery(
    {
      testPlanId: testPlanId ?? "",
      is_archive: userConfig?.test_plans?.is_show_archived,
      project: project.id,
      parent: null,
    },
    {
      skip: !testPlanId,
    }
  )

  useEffect(() => {
    const pathSegments = location.pathname.split("/")
    const lastSegment = pathSegments[pathSegments.length - 1]

    setTab(tabKeys.includes(lastSegment) ? (lastSegment as TestPlanTabs) : "overview")
  }, [location.pathname])

  const handleTabChange = (newTab: string) => {
    setTab(newTab as TestPlanTabs)
    if (newTab === "overview") {
      navigate(`/projects/${project.id}/plans/${testPlanId}`)
      return
    }

    navigate(`/projects/${project.id}/plans/${testPlanId}/${newTab}`)
  }

  const tabItems: TabsProps["items"] = [
    {
      key: "overview",
      label: t("Overview"),
    },
    {
      key: "activity",
      label: t("Activity"),
    },
    {
      key: "custom-attributes",
      label: t("Custom Attributes"),
    },
    // {
    //   key: "attachments",
    //   label: t("Attachments"),
    // },
  ]

  return (
    <TestPlanContext.Provider
      value={{ testPlan, isFetching, refetch, hasTestPlan: !!testPlanId && !!testPlan }}
    >
      <TestsTreeProvider>
        <TestPlanHeader />
        {testPlanId && (
          <Tabs
            defaultActiveKey="overview"
            activeKey={tab}
            items={tabItems}
            onChange={handleTabChange}
            style={{ marginBottom: 24 }}
          />
        )}
        <Outlet />
      </TestsTreeProvider>
    </TestPlanContext.Provider>
  )
}

export const useTestPlanContext = () => {
  return useContext(TestPlanContext)!
}
