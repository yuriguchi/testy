import { TableProps } from "antd"
import { TablePaginationConfig } from "antd/es/table"
import { ColumnsType } from "antd/lib/table"
import { FilterValue } from "antd/lib/table/interface"
import dayjs from "dayjs"
import { useStatuses } from "entities/status/model/use-statuses"
import { useContext, useEffect, useState } from "react"
import { useTranslation } from "react-i18next"
import { Link, useParams } from "react-router-dom"

import { useLazyGetTestPlanActivityQuery } from "entities/test-plan/api"
import { filterActionFormat } from "entities/test-plan/lib"

import { UserAvatar } from "entities/user/ui"

import { ProjectContext } from "pages/project"

import { useTableSearch } from "shared/hooks"
import { antdSorterToTestySort } from "shared/libs"
import { HighLighterTesty, Status } from "shared/ui"
import { UntestedStatus } from "shared/ui/status"

import { useTestPlanActivityBreadcrumbs } from "./index"

interface TableParams {
  pagination?: TablePaginationConfig
  filters?: Record<string, FilterValue>
  sorter?: string
  search?: string
}

const initialTableParams: TableParams = {
  pagination: {
    current: 1,
    pageSize: 10,
    pageSizeOptions: ["10", "100", "200", "500", "1000"],
    showLessItems: true,
  },
}

export const useTestPlanActivity = () => {
  const { t } = useTranslation()
  const { project } = useContext(ProjectContext)!
  const { testPlanId } = useParams<ParamTestPlanId>()
  const { statusesFilters } = useStatuses({
    project: project.id,
    plan: testPlanId,
    isActivity: true,
  })
  const [getActivity, { data, isLoading }] = useLazyGetTestPlanActivityQuery()
  const { getColumnSearch, setSearchText, setSearchedColumn, searchText, searchedColumn } =
    useTableSearch()
  const { renderBreadCrumbs } = useTestPlanActivityBreadcrumbs()
  const [filteredInfo, setFilteredInfo] = useState<Record<string, FilterValue | null>>({})
  const [tableParams, setTableParams] = useState<TableParams>(initialTableParams)

  const columns: ColumnsType<TestPlanActivityResult> = [
    {
      title: t("Time"),
      dataIndex: "action_timestamp",
      key: "action_timestamp",
      width: "100px",
      sorter: (a, b) => dayjs(a.action_timestamp).diff(b.action_timestamp),
      render: (value: string, record) => (
        <div data-testid={`test-plan-activity-time-${record.test_name}`}>
          {dayjs(value).format("HH:mm:ss")}
        </div>
      ),
    },
    {
      title: t("Test"),
      dataIndex: "test_name",
      key: "test_name",
      ...getColumnSearch("test_name"),
      render: (text: string, record) =>
        searchedColumn.some((i) => i === "test_name") ? (
          <Link
            to={`/projects/${project.id}/plans/${record.breadcrumbs.id}?test=${record.test_id}`}
            data-testid={`test-plan-activity-test-link-${record.test_name}`}
          >
            <HighLighterTesty searchWords={searchText} textToHighlight={text} />
          </Link>
        ) : (
          <Link
            to={`/projects/${project.id}/plans/${record.breadcrumbs.id}?test=${record.test_id}`}
            data-testid={`test-plan-activity-test-link-${record.test_name}`}
          >
            {text}
          </Link>
        ),
      onFilter: (value, record) =>
        record.test_name.toLowerCase().includes(String(value).toLowerCase()),
    },
    {
      title: t("Test Plans"),
      dataIndex: "breadcrumbs",
      key: "breadcrumbs",
      width: "500px",
      render: (value: BreadCrumbsActivityResult) => renderBreadCrumbs(value),
    },
    {
      title: t("Action"),
      dataIndex: "action",
      key: "action",
      width: "150px",
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
      onFilter: (value, record) => record.action.includes(String(value)),
      render: (action: TestPlanActivityAction, record) => (
        <div data-testid={`test-plan-activity-action-${record.test_name}`}>{t(action)}</div>
      ),
    },
    {
      title: t("Status"),
      dataIndex: "status",
      key: "status",
      width: "150px",
      filters: statusesFilters,
      render: (last_status: string[], record) => {
        if (!last_status) {
          return <UntestedStatus />
        }
        return <Status id={record.status} name={record.status_text} color={record.status_color} />
      },
      onFilter: (value, record) => record.status === value,
    },
    {
      title: t("User"),
      dataIndex: "username",
      key: "username",
      width: "240px",
      ...getColumnSearch("username"),
      onFilter: (value, record) =>
        record.username.toLowerCase().includes(String(value).toLowerCase()),
      render: (_, record) => {
        return (
          <div
            style={{ display: "flex", alignItems: "center", flexDirection: "row", gap: 8 }}
            data-testid={`test-plan-activity-user-${record.test_name}`}
          >
            <UserAvatar size={32} avatar_link={record.avatar_link} />
            {record.username}
          </div>
        )
      },
    },
  ]

  useEffect(() => {
    setSearchedColumn(["user", "test_name"])
  }, [])

  useEffect(() => {
    if (!testPlanId) return

    const requestData = {
      testPlanId,
      page_size: tableParams.pagination?.pageSize,
      page: tableParams.pagination?.current,
      status: tableParams.filters?.status,
      history_type: tableParams.filters?.action
        ? filterActionFormat((tableParams.filters.action as string[]) ?? [])
        : undefined,
      search: tableParams.search ? tableParams.search : undefined,
      ordering: tableParams.sorter ? tableParams.sorter : undefined,
    }

    getActivity(requestData)
  }, [testPlanId, searchText, JSON.stringify(tableParams)])

  const handlePaginationChange = (page: number, pageSize: number) => {
    if (!testPlanId) return
    setTableParams((prevState) => ({
      ...prevState,
      pagination: {
        ...prevState.pagination,
        pageSize,
        current: page,
      },
    }))
  }

  const handleSearch = (value: string) => {
    if (!testPlanId) return
    setTableParams((prevState) => ({
      ...prevState,
      search: value,
    }))
    setSearchText(value)
  }

  const handleSearchChange = (value: string) => {
    setSearchText(value)
  }

  const handleTableChange: TableProps<TestPlanActivityResult>["onChange"] = (
    pagination: TablePaginationConfig,
    filters: Record<string, FilterValue | null>,
    sorter
  ) => {
    const sortTesty = antdSorterToTestySort(sorter, "plans")

    if (filters?.status === null) {
      delete filters.status
    }

    setTableParams((prevState) => ({
      ...prevState,
      pagination,
      filters: filters as Record<string, FilterValue>,
      sorter: sortTesty,
    }))
    setFilteredInfo(filters)
  }

  const clearFilters = () => {
    setFilteredInfo({})
    setTableParams((prevState) => ({
      ...initialTableParams,
      sorter: prevState.sorter,
    }))
    setSearchText("")
  }

  return {
    data,
    isLoading,
    columns,
    searchText,
    filteredInfo,
    pagination: tableParams.pagination,
    handlePaginationChange,
    handleSearch,
    handleSearchChange,
    handleTableChange,
    clearFilters,
  }
}
