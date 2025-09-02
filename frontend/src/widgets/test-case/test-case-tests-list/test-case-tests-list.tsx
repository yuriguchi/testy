import { Table } from "antd"
import { TableProps } from "antd/es/table"
import { ColumnsType, TablePaginationConfig } from "antd/lib/table"
import { FilterValue } from "antd/lib/table/interface"
import { useStatuses } from "entities/status/model/use-statuses"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Link, useParams } from "react-router-dom"

import { useGetTestCaseTestsListQuery } from "entities/test-case/api"

import { useTestPlanActivityBreadcrumbs } from "entities/test-plan/model"

import { UserAvatar, UserUsername } from "entities/user/ui"

import { antdSorterToTestySort } from "shared/libs"
import { Status } from "shared/ui"
import { UntestedStatus } from "shared/ui/status"

interface TableParams {
  sorter: string
  filters: Record<string, FilterValue | null>
}

interface Props {
  testCase: TestCase
  isShowArchive: boolean
}

export const TestCaseTestsList = ({ testCase, isShowArchive }: Props) => {
  const { t } = useTranslation()
  const { projectId } = useParams<ParamProjectId>()
  const { renderBreadCrumbs } = useTestPlanActivityBreadcrumbs()
  const [tableParams, setTableParams] = useState<TableParams>({ sorter: "", filters: {} })
  const [pagination, setPagination] = useState({
    page: 1,
    page_size: 5,
  })

  const { statusesFiltersWithUntested } = useStatuses({ project: projectId })

  const { data, isFetching } = useGetTestCaseTestsListQuery(
    {
      testCaseId: testCase.id,
      page: pagination.page,
      page_size: pagination.page_size,
      ordering: tableParams.sorter ? tableParams.sorter : "",
      last_status: tableParams.filters?.last_status?.join(",") ?? undefined,
      is_archive: isShowArchive,
    },
    {
      refetchOnMountOrArgChange: true,
    }
  )

  const handlePaginationChange = (page: number, page_size: number) => {
    setPagination({ page, page_size })
  }

  const columns: ColumnsType<TestsWithPlanBreadcrumbs> = [
    {
      title: t("ID"),
      dataIndex: "id",
      key: "id",
      width: "70px",
      sorter: true,
      render: (_, record) => (
        <Link to={`/projects/${record.project}/plans/${record.plan}?test=${record.id}`}>
          {record.id}
        </Link>
      ),
    },
    {
      title: t("Test Plan"),
      dataIndex: "breadcrumbs",
      key: "breadcrumbs",
      render: (value: BreadCrumbsActivityResult) => renderBreadCrumbs(value),
    },
    {
      title: t("Last status"),
      dataIndex: "last_status",
      key: "last_status",
      width: "150px",
      filters: statusesFiltersWithUntested,
      render: (last_status, record) => {
        if (!last_status) {
          return <UntestedStatus />
        }
        return (
          <Status
            id={record.last_status}
            name={record.last_status_name}
            color={record.last_status_color}
          />
        )
      },
    },
    {
      title: t("Assignee"),
      dataIndex: "assignee_username",
      key: "assignee_username",
      sorter: true,
      render: (_, record) => {
        if (!record.assignee_username) {
          return <span style={{ opacity: 0.7 }}>{t("Nobody")}</span>
        }

        return (
          <div style={{ display: "flex", alignItems: "center", flexDirection: "row", gap: 8 }}>
            <UserAvatar size={32} avatar_link={record.avatar_link} />
            <UserUsername username={record.assignee_username} />
          </div>
        )
      },
    },
  ]

  const handleChange: TableProps<TestsWithPlanBreadcrumbs>["onChange"] = (
    _: TablePaginationConfig,
    filters: Record<string, FilterValue | null>,
    sorter
  ) => {
    const testySorting = antdSorterToTestySort(sorter, "tests")
    setTableParams({ sorter: testySorting, filters })
  }

  return (
    <>
      <Table
        dataSource={data?.results ?? []}
        style={{ cursor: "pointer" }}
        columns={columns}
        pagination={{
          onChange: handlePaginationChange,
          pageSize: pagination.page_size,
          current: pagination.page,
          total: data?.count ?? 0,
        }}
        size="small"
        onChange={handleChange}
        rowKey="id"
        loading={isFetching}
      />
    </>
  )
}
