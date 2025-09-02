import { Flex, Tooltip, Typography } from "antd"
import { TableProps } from "antd/es/table"
import { ColumnsType, TablePaginationConfig } from "antd/lib/table"
import { FilterValue } from "antd/lib/table/interface"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"

import { useGetProjectsQuery } from "entities/project/api"
import { ProjectIcon } from "entities/project/ui"

import { config } from "shared/config"
import { useTableSearch } from "shared/hooks"
import { ArchivedTag, HighLighterTesty } from "shared/ui"

const { Link } = Typography

export const useProjectsTable = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { setSearchText, getColumnSearch, searchText } = useTableSearch()
  const [filteredInfo, setFilteredInfo] = useState<Record<string, FilterValue | null>>({})
  const [isShowArchive, setIsShowArchive] = useState(false)
  const [paginationParams, setPaginationParams] = useState({
    page: 1,
    pageSize: 10,
  })

  const { data: projects, isFetching } = useGetProjectsQuery({
    is_archive: isShowArchive,
    page: paginationParams.page,
    page_size: paginationParams.pageSize,
    name: searchText || undefined,
  })

  const handleClearAll = () => {
    setFilteredInfo({})
    setSearchText("")
    setIsShowArchive(false)
  }

  const handleShowProjectDetail = (projectId: Id) => {
    navigate(`/administration/projects/${projectId}/overview`)
  }

  const handleChange: TableProps<Project>["onChange"] = (
    pagination: TablePaginationConfig,
    filters: Record<string, FilterValue | null>
  ) => {
    setFilteredInfo(filters)
  }

  const handleRowClick = (record: Project) => {
    if (record.is_private && !record.is_manageable) {
      return
    }
    navigate(`/administration/projects/${record.id}/overview`)
  }

  const columns: ColumnsType<Project> = [
    {
      title: t("Icon"),
      dataIndex: "icon",
      key: "icon",
      width: 50,
      render: (text, record) => (
        <ProjectIcon
          icon={record.icon}
          name={record.name}
          dataTestId="administration-table-project-icon"
        />
      ),
    },
    {
      title: t("Name"),
      dataIndex: "name",
      key: "name",
      filteredValue: filteredInfo.name ?? null,
      ...getColumnSearch("name"),
      onFilter: (value, record) => record.name.toLowerCase().includes(String(value).toLowerCase()),
      render: (text: string, record) => {
        const handleLinkClick = () => {
          if (!record.is_private || record.is_manageable) {
            handleShowProjectDetail(record.id)
          }
        }

        const linkEl = (
          <Flex gap={8} align="center">
            {record.is_archive && <ArchivedTag />}
            <Link onClick={handleLinkClick}>
              <HighLighterTesty searchWords={searchText} textToHighlight={text} />
            </Link>
          </Flex>
        )

        if (record.is_private && !record.is_manageable) {
          return (
            <Tooltip placement="topLeft" title={t("You are not able to manage this project")} arrow>
              {linkEl}
            </Tooltip>
          )
        }

        return linkEl
      },
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
    isShowArchive,
    handleRowClick,
    handleChange,
    handleClearAll,
    handleShowArchive: setIsShowArchive,
  }
}
