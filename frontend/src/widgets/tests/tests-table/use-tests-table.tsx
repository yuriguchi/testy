import { ColumnsType } from "antd/es/table"
import { FilterValue, RowSelectMethod } from "antd/es/table/interface"
import { TablePaginationConfig } from "antd/lib"
import dayjs from "dayjs"
import { Key, useContext, useEffect, useMemo } from "react"
import { useTranslation } from "react-i18next"
import { Link, useSearchParams } from "react-router-dom"

import { useAppDispatch, useAppSelector } from "app/hooks"

import { Label } from "entities/label/ui"

import { useGetTestsQuery } from "entities/test/api"
import {
  selectDrawerTest,
  selectFilter,
  selectOrdering,
  selectSettings,
  setDrawerTest,
  setPagination,
  updateSettings,
} from "entities/test/model"

import { useGetTestPlanTestsQuery } from "entities/test-plan/api"

import { UserAvatar, UserUsername } from "entities/user/ui"

import { ProjectContext } from "pages/project"

import { colors, config } from "shared/config"
import { paginationSchema } from "shared/config/query-schemas"
import { NOT_ASSIGNED_FILTER_VALUE } from "shared/constants"
import { useUrlSyncParams } from "shared/hooks"
import { ArchivedTag, HighLighterTesty, Status } from "shared/ui"
import { UntestedStatus } from "shared/ui/status"

import styles from "./styles.module.css"

interface Props {
  testPlanId: Id | null
}

export const useTestsTable = ({ testPlanId }: Props) => {
  const { t } = useTranslation()
  const { project } = useContext(ProjectContext)!
  const [searchParams, setSearchParams] = useSearchParams()
  const dispatch = useAppDispatch()

  const drawerTest = useAppSelector(selectDrawerTest)
  const testsFilter = useAppSelector(selectFilter)
  const testsOrdering = useAppSelector(selectOrdering)
  const tableSettings = useAppSelector(selectSettings<TestTableParams>("table"))

  const reqParams = useMemo(() => {
    return {
      ...testsFilter,
      testPlanId: tableSettings.testPlanId ?? testPlanId,
      ordering: testsOrdering,
      page: tableSettings.page,
      page_size: tableSettings.page_size,
    }
  }, [tableSettings, testsOrdering, testsFilter])

  useEffect(() => {
    dispatch(
      updateSettings({
        key: "table",
        settings: {
          testPlanId,
        },
      })
    )

    return () => {
      dispatch(
        updateSettings({
          key: "table",
          settings: {
            page: 1,
          },
        })
      )
    }
  }, [testPlanId])

  const syncObject = { page: tableSettings.page, page_size: tableSettings.page_size }
  useUrlSyncParams({
    params: syncObject as unknown as Record<string, unknown>,
    queryParamsSchema: paginationSchema,
    updateParams: (params) => {
      const paramsData = params as { page?: number; page_size?: number }
      dispatch(
        setPagination({
          key: "table",
          pagination: {
            page: paramsData?.page ?? 1,
            page_size: paramsData?.page_size ?? tableSettings.page_size,
          },
        })
      )
    },
  })

  const queryParams = {
    project: project.id,
    testPlanId: reqParams.testPlanId ?? undefined,
    nested_search: true,
    is_archive: reqParams.is_archive,
    labels: reqParams.labels,
    not_labels: reqParams.not_labels,
    labels_condition: reqParams.labels_condition,
    suite: reqParams.suites,
    plan: reqParams.plans,
    last_status: reqParams.statuses,
    ordering: reqParams.ordering,
    page: reqParams.page,
    page_size: reqParams.page_size,
    assignee: reqParams.assignee.filter((assignee) => assignee !== NOT_ASSIGNED_FILTER_VALUE),
    unassigned: reqParams.assignee.includes("null") ? true : undefined,
    search: reqParams.name_or_id,
    show_descendants: true,
    test_plan_started_before: reqParams.test_plan_started_before,
    test_plan_started_after: reqParams.test_plan_started_after,
    test_plan_created_before: reqParams.test_plan_created_before,
    test_plan_created_after: reqParams.test_plan_created_after,
    test_created_before: reqParams.test_created_before,
    test_created_after: reqParams.test_created_after,
    _n: reqParams._n,
  }

  const { data: testPlanData, isFetching: isFetchingTestPlan } = useGetTestPlanTestsQuery(
    queryParams,
    {
      skip: !reqParams.testPlanId,
    }
  )

  const { data: rootTestsData, isFetching: isRootTestsFetching } = useGetTestsQuery(queryParams, {
    skip: !!reqParams.testPlanId,
  })

  const data = reqParams.testPlanId ? testPlanData : rootTestsData
  const isFetching = reqParams.testPlanId ? isFetchingTestPlan : isRootTestsFetching

  useEffect(() => {
    if (tableSettings.isAllSelectedTableBulk && data?.results) {
      const newSelectedRows = data.results
        .map((test) => test.id)
        .filter((id) => !tableSettings.excludedRows.includes(id))
      dispatch(
        updateSettings({
          key: "table",
          settings: {
            selectedRows: newSelectedRows,
          },
        })
      )
    }
  }, [data])

  const handleTableChange = (pagination: TablePaginationConfig) => {
    dispatch(
      updateSettings({
        key: "table",
        settings: {
          page: pagination.current,
          page_size: pagination.pageSize,
        },
      })
    )
  }

  const handleRowClick = (testClick: Test) => {
    searchParams.set("test", String(testClick.id))
    setSearchParams(searchParams)
    dispatch(setDrawerTest(testClick))
  }

  const handleSelectRows = (
    selectedRowKeys: Key[],
    selectedRows: Test[],
    info: {
      type: RowSelectMethod
    }
  ) => {
    dispatch(
      updateSettings({
        key: "table",
        settings: {
          selectedRows: selectedRowKeys as number[],
          hasBulk: !!selectedRowKeys.length,
        },
      })
    )

    if (info.type === "all") {
      const newIsAllSelected = !tableSettings.isAllSelectedTableBulk
      dispatch(
        updateSettings({
          key: "table",
          settings: {
            excludedRows: [],
            isAllSelectedTableBulk: newIsAllSelected,
          },
        })
      )
      if (!newIsAllSelected) {
        dispatch(
          updateSettings({
            key: "table",
            settings: {
              selectedRows: [],
              hasBulk: false,
            },
          })
        )
      } else {
        dispatch(
          updateSettings({
            key: "table",
            settings: {
              selectedRows: data?.results.map((test) => test.id) ?? [],
            },
          })
        )
      }
    } else {
      if (tableSettings.isAllSelectedTableBulk) {
        //Exclude
        const notThisPageExcluded = tableSettings.excludedRows.filter(
          (id) => !data?.results.find((test) => test.id === id)
        )
        const currentPageExcluded =
          data?.results
            .filter((test) => !selectedRowKeys.includes(test.id))
            .map((test) => test.id) ?? []

        dispatch(
          updateSettings({
            key: "table",
            settings: {
              excludedRows: [...notThisPageExcluded, ...currentPageExcluded],
              hasBulk: true,
            },
          })
        )
      }
    }
  }

  const columns: ColumnsType<Test> = useMemo(() => {
    return (
      [
        {
          title: t("ID"),
          dataIndex: "id",
          key: "id",
          width: "70px",
        },
        {
          title: t("Name"),
          dataIndex: "name",
          key: "name",
          render: (text: string, record) => {
            const newQueryParams = new URLSearchParams(location.search)
            newQueryParams.delete("test")

            return (
              <Link
                id={record.name}
                to={`/projects/${record.project}/plans/${testPlanId ?? ""}?test=${record.id}${newQueryParams.size ? `&${newQueryParams.toString()}` : ""}`}
                className={styles.link}
                onClick={(e) => {
                  e.stopPropagation()
                  dispatch(setDrawerTest(record))
                }}
              >
                {record.is_archive && <ArchivedTag />}
                <HighLighterTesty searchWords={testsFilter.name_or_id} textToHighlight={text} />
              </Link>
            )
          },
        },
        {
          title: t("Test Plan"),
          dataIndex: "plan_path",
          key: "plan_path",
        },
        {
          title: t("Test Suite"),
          dataIndex: "suite_path",
          key: "suite_path",
        },
        {
          title: t("Estimate"),
          dataIndex: "estimate",
          key: "estimate",
          width: "100px",
          render: (estimate: string | null) => estimate ?? "-",
        },
        {
          title: t("Labels"),
          dataIndex: "labels",
          key: "labels",
          render: (labels: Test["labels"]) => (
            <ul className={styles.list}>
              {labels.map((label) => (
                <li key={label.id}>
                  <Label content={label.name} color={colors.accent} />
                </li>
              ))}
            </ul>
          ),
        },
        {
          title: t("Last status"),
          dataIndex: "last_status",
          key: "last_status",
          width: "150px",
          filteredValue: (testsFilter.statuses as FilterValue) ?? null,
          render: (value, record) => {
            if (!value) {
              return <UntestedStatus />
            }
            return (
              <Status
                name={record.last_status_name}
                color={record.last_status_color}
                id={record.last_status}
              />
            )
          },
        },
        {
          title: t("Assignee"),
          dataIndex: "assignee_username",
          key: "assignee_username",
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
        {
          title: t("Created At"),
          dataIndex: "created_at",
          key: "created_at",
          width: 150,
          render: (value: string) => dayjs(value).format("YYYY-MM-DD HH:mm"),
        },
      ] as ColumnsType<Test>
    ).filter((col) => tableSettings.visibleColumns.some((i) => i.key === col.key))
  }, [testsFilter, tableSettings])

  const paginationTable: TablePaginationConfig = {
    hideOnSinglePage: false,
    pageSizeOptions: config.pageSizeOptions,
    showLessItems: true,
    showSizeChanger: true,
    current: tableSettings.page,
    pageSize: tableSettings.page_size,
    total: data?.count ?? 0,
  }

  return {
    activeTestId: drawerTest?.id,
    data: data?.results,
    columns,
    isLoading: isFetching,
    paginationTable,
    selectedRows: tableSettings.selectedRows,
    handleTableChange,
    handleRowClick,
    handleSelectRows,
  }
}
