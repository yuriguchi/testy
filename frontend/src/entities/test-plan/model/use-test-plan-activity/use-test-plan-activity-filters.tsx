import Search from "antd/lib/input/Search"
import { ColumnsType } from "antd/lib/table"
import { useStatuses } from "entities/status/model/use-statuses"
import { useContext } from "react"
import { useTranslation } from "react-i18next"
import { useParams } from "react-router-dom"

import { ProjectContext } from "pages/project"

import { useTestPlanActivity } from "./use-test-plan-activity"

export const useTestPlanActivityFilters = (
  testPlanActivity: ReturnType<typeof useTestPlanActivity>
) => {
  const { t } = useTranslation()
  const { project } = useContext(ProjectContext)!
  const { testPlanId } = useParams<ParamTestPlanId & ParamProjectId>()
  const { statusesFilters } = useStatuses({
    project: project.id,
    plan: testPlanId,
    isActivity: true,
  })
  const filters: ColumnsType<TestPlanActivityResult> = [
    {
      title: t("Time"),
      dataIndex: "action_timestamp",
      key: "action_timestamp",
      width: "150px",
      sorter: true,
      filteredValue: testPlanActivity.filteredInfo?.action_timestamp ?? null,
    },
    {
      title: t("Action"),
      dataIndex: "action",
      key: "action",
      width: "150px",
      filteredValue: testPlanActivity.filteredInfo?.action ?? null,
      filters: [
        {
          value: "added",
          text: t("added"),
        },
        {
          value: "deleted",
          text: t("deleted"),
        },
        {
          value: "updated",
          text: t("updated"),
        },
      ],
    },
    {
      title: t("Status"),
      dataIndex: "status",
      key: "status",
      width: "150px",
      filteredValue: testPlanActivity.filteredInfo?.status ?? null,
      filters: statusesFilters,
    },
    {
      title: (
        <Search
          placeholder={t("Search by test or user")}
          onSearch={testPlanActivity.handleSearch}
          value={testPlanActivity.searchText}
          onChange={(e) => testPlanActivity.handleSearchChange(e.target.value)}
          data-testid="test-plan-activity-search"
        />
      ),
    },
  ]

  return {
    filters,
    handleChange: testPlanActivity.handleTableChange,
  }
}
