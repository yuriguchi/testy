import { Flex, Space, Tooltip, Typography } from "antd"
import { TableProps } from "antd/es/table"
import { ColumnsType, TablePaginationConfig } from "antd/lib/table"
import { FilterValue } from "antd/lib/table/interface"
import { MeContext } from "processes"
import { useContext, useState } from "react"
import { useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"

import { useGetProjectsQuery } from "entities/project/api"
import { ProjectIcon } from "entities/project/ui"

import { FolowProject, RequestProjectAccess } from "features/project"

import { icons } from "shared/assets/inner-icons"
import { config } from "shared/config"
import { antdSorterToTestySort } from "shared/libs"
import { ArchivedTag, HighLighterTesty } from "shared/ui"
import { CheckedIcon } from "shared/ui/icons"

import styles from "./styles.module.css"

const { DashboardIcon, TestPlansIcon, TestSuitesIcon } = icons

const { Link } = Typography

export const useProjectsDashboardTable = ({ searchName }: { searchName: string }) => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { userConfig } = useContext(MeContext)
  const [filteredInfo, setFilteredInfo] = useState<Record<string, FilterValue | null>>({})
  const [paginationParams, setPaginationParams] = useState({
    page: 1,
    pageSize: 10,
  })
  const [ordering, setOrdering] = useState("is_private")

  const { data: projects, isFetching } = useGetProjectsQuery(
    {
      is_archive: userConfig?.projects?.is_show_archived,
      favorites: userConfig?.projects?.is_only_favorite ?? false,
      page: paginationParams.page,
      page_size: paginationParams.pageSize,
      name: searchName,
      ordering: ordering.length ? ordering : "is_private",
    },
    {
      skip: !userConfig,
    }
  )

  const handleActionClick = (projectId: number, type: "overview" | "suites" | "plans") => {
    navigate(`/projects/${projectId}/${type}`)
  }

  const handleChange: TableProps<Project>["onChange"] = (
    pagination: TablePaginationConfig,
    filters: Record<string, FilterValue | null>,
    sorter
  ) => {
    const isPrivate = antdSorterToTestySort<Project>(sorter)
    setOrdering(isPrivate)
    setFilteredInfo(filters)
  }

  const columns: ColumnsType<Project> = [
    {
      key: "action_1",
      width: 64,
      render: (_, record) => (
        <Flex>
          <FolowProject project={record} />
          {record.is_archive ? (
            <Flex style={{ height: 30 }} align="center">
              <ArchivedTag />
            </Flex>
          ) : null}
        </Flex>
      ),
    },
    {
      title: t("Icon"),
      dataIndex: "icon",
      key: "icon",
      width: 50,
      render: (text, record) => (
        <ProjectIcon
          icon={record.icon}
          name={record.name}
          dataTestId="dashboard-table-project-icon"
        />
      ),
    },
    {
      title: t("Name"),
      dataIndex: "name",
      key: "name",
      filteredValue: filteredInfo.name ?? null,
      onFilter: (value, record) => record.name.toLowerCase().includes(String(value).toLowerCase()),
      render: (text, record) => {
        const handleLinkClick = () => {
          if (!record.is_private || record.is_manageable) {
            handleActionClick(record.id, "overview")
          }
        }

        const linkEl = (
          <Link onClick={handleLinkClick}>
            {/* eslint-disable-next-line @typescript-eslint/no-unsafe-assignment*/}
            <HighLighterTesty searchWords={searchName} textToHighlight={text} />
          </Link>
        )

        if (record.is_private && !record.is_visible) {
          return (
            <Tooltip placement="topLeft" title={t("You are not able to view this project")} arrow>
              {linkEl}
            </Tooltip>
          )
        }

        return linkEl
      },
    },
    {
      title: t("Test Suites"),
      dataIndex: "suites_count",
      key: "suites_count",
      render: (value: string, record) => (record.is_visible ? value : "-"),
    },
    {
      title: t("Test Cases"),
      dataIndex: "cases_count",
      key: "cases_count",
      render: (value: string, record) => (record.is_visible ? value : "-"),
    },
    {
      title: t("Test Plans"),
      dataIndex: "plans_count",
      key: "plans_count",
      render: (value: string, record) => (record.is_visible ? value : "-"),
    },
    {
      title: t("Tests"),
      dataIndex: "tests_count",
      key: "tests_count",
      render: (value: string, record) => (record.is_visible ? value : "-"),
    },
    {
      title: t("Is Private"),
      dataIndex: "is_private",
      key: "is_private",
      width: 120,
      render: (is_private: boolean) => <CheckedIcon value={is_private} />,
      sorter: true,
    },
    {
      key: "action",
      width: 128,
      render: (_, record) =>
        record.is_visible ? (
          <Space className={styles.action}>
            <Tooltip title={t("Overview")} placement="top">
              <DashboardIcon onClick={() => handleActionClick(record.id, "overview")} />
            </Tooltip>
            <Tooltip title={t("Test Suites")} placement="top">
              <TestSuitesIcon onClick={() => handleActionClick(record.id, "suites")} />
            </Tooltip>
            <Tooltip title={t("Test Plans")} placement="top">
              <TestPlansIcon onClick={() => handleActionClick(record.id, "plans")} />
            </Tooltip>
          </Space>
        ) : (
          <RequestProjectAccess project={record} type="min" />
        ),
    },
  ]

  const handlePaginationChange = (page: number, pageSize: number) => {
    setPaginationParams({ page, pageSize })
  }

  const paginationTable: TablePaginationConfig = {
    hideOnSinglePage: false,
    pageSizeOptions: config.pageSizeOptions,
    showLessItems: true,
    showSizeChanger: true,
    current: paginationParams.page,
    pageSize: paginationParams.pageSize,
    total: projects?.count ?? 0,
    onChange: handlePaginationChange,
  }

  return {
    columns,
    projects,
    isLoading: isFetching,
    paginationTable,
    handleChange,
  }
}
