import { TablePaginationConfig } from "antd"
import { ColumnsType } from "antd/lib/table"
import dayjs from "dayjs"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { Link, useParams, useSearchParams } from "react-router-dom"

import { useAppDispatch, useAppSelector } from "app/hooks"

import { Label } from "entities/label/ui"

import { useGetSuiteTestCasesQuery } from "entities/suite/api"

import { useGetTestPlanTestCasesQuery } from "entities/test-case/api"
import {
  selectDrawerTestCase,
  selectFilter,
  selectOrdering,
  selectSettings,
  setDrawerTestCase,
  setPagination,
  updateSettings,
} from "entities/test-case/model"

import { colors, config } from "shared/config"
import { paginationSchema } from "shared/config/query-schemas"
import { useUrlSyncParams } from "shared/hooks"
import { ArchivedTag, HighLighterTesty } from "shared/ui"

import styles from "./styles.module.css"

export const useTestCasesTable = () => {
  const { t } = useTranslation()
  const { testSuiteId, projectId } = useParams<ParamTestSuiteId & ParamProjectId>()
  const dispatch = useAppDispatch()
  const [searchParams, setSearchParams] = useSearchParams()

  const testCasesFilter = useAppSelector(selectFilter)
  const testCasesOrdering = useAppSelector(selectOrdering)
  const tableSettings = useAppSelector(selectSettings<TestTableParams>("table"))

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
    project: projectId ?? "",
    suite: testCasesFilter.suites,
    is_archive: testCasesFilter.is_archive,
    labels: testCasesFilter.labels,
    not_labels: testCasesFilter.not_labels,
    labels_condition: testCasesFilter.labels_condition,
    page: tableSettings.page,
    page_size: tableSettings.page_size,
    ordering: testCasesOrdering,
    search: testCasesFilter.name_or_id,
    show_descendants: true,
    _n: testCasesFilter._n,
  }

  const { data: suitesData, isFetching: isSuitesFetching } = useGetSuiteTestCasesQuery(
    {
      testSuiteId: Number(testSuiteId),
      ...queryParams,
    },
    {
      skip: !projectId || !testSuiteId,
    }
  )
  const { data: suitesFromRoot, isFetching: isSuitesFromRootFetching } =
    useGetTestPlanTestCasesQuery(queryParams, {
      skip: !projectId || !!testSuiteId,
    })

  const data = testSuiteId ? suitesData : suitesFromRoot
  const isFetching = testSuiteId ? isSuitesFetching : isSuitesFromRootFetching

  const handleRowClick = (testCase: TestCase) => {
    searchParams.set("test_case", String(testCase.id))
    setSearchParams(searchParams)
    dispatch(setDrawerTestCase(testCase))
  }

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

  const selectedTestCase = useAppSelector(selectDrawerTestCase)

  const paginationTable: TablePaginationConfig = {
    hideOnSinglePage: false,
    pageSizeOptions: config.pageSizeOptions,
    showLessItems: true,
    showSizeChanger: true,
    current: tableSettings.page,
    pageSize: tableSettings.page_size,
    total: data?.count ?? 0,
  }

  const columns: ColumnsType<TestCase> = useMemo(() => {
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
            newQueryParams.delete("test_case")

            return (
              <Link
                id={record.name}
                to={`/projects/${record.project}/suites/${testSuiteId ?? ""}?test_case=${record.id}${newQueryParams.size ? `&${newQueryParams.toString()}` : ""}`}
                className={styles.link}
                onClick={(e) => {
                  e.stopPropagation()
                  dispatch(setDrawerTestCase(record))
                }}
              >
                {record.is_archive && <ArchivedTag />}
                <HighLighterTesty searchWords={testCasesFilter.name_or_id} textToHighlight={text} />
              </Link>
            )
          },
        },
        {
          title: t("Test Suite"),
          dataIndex: "suite_path",
          key: "suite_path",
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
          title: t("Estimate"),
          dataIndex: "estimate",
          key: "estimate",
          width: "100px",
          render: (estimate: string | null) => estimate ?? "-",
        },
        {
          title: t("Created At"),
          dataIndex: "created_at",
          key: "created_at",
          width: 150,
          render: (value: string) => dayjs(value).format("YYYY-MM-DD HH:mm"),
        },
      ] as ColumnsType<TestCase>
    ).filter((col) => tableSettings.visibleColumns.some((i) => i.key === col.key))
  }, [testCasesFilter, tableSettings, testSuiteId])

  return {
    data: data?.results,
    columns,
    isLoading: isFetching,
    selectedTestCase,
    paginationTable,
    handleTableChange,
    handleRowClick,
  }
}
