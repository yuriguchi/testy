import { Button, Space, Table, TableProps } from "antd"
import { ColumnsType } from "antd/es/table"
import type { FilterValue, TablePaginationConfig } from "antd/es/table/interface"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { useParams } from "react-router-dom"

import { useGetLabelsQuery } from "entities/label/api"
import { getLabelTypeTextByNumber } from "entities/label/lib"

import { DeleteLabelButton, EditLabelButton } from "features/label"

import { useTableSearch } from "shared/hooks"

export const LabelsTable = () => {
  const { t } = useTranslation()
  const { projectId } = useParams<ParamProjectId>()

  const { data: labels, isFetching } = useGetLabelsQuery(
    { project: projectId ?? "" },
    { skip: !projectId }
  )

  const [filteredInfo, setFilteredInfo] = useState<Record<string, FilterValue | null>>({})
  const { setSearchText, getColumnSearch } = useTableSearch()

  const handleChange: TableProps<Label>["onChange"] = (
    pagination: TablePaginationConfig,
    filters: Record<string, FilterValue | null>
  ) => {
    setFilteredInfo(filters)
  }

  const clearAll = () => {
    setFilteredInfo({})
    setSearchText("")
  }

  const columns: ColumnsType<Label> = [
    {
      title: t("ID"),
      dataIndex: "id",
      key: "id",
      width: "70px",
      sorter: (a, b) => Number(a.id) - Number(b.id),
    },
    {
      title: t("Name"),
      dataIndex: "name",
      key: "name",
      filteredValue: filteredInfo.name ?? null,
      sorter: (a, b) => a.name.localeCompare(b.name),
      ...getColumnSearch("name"),
      onFilter: (value, record) => record.name.toLowerCase().includes(String(value).toLowerCase()),
    },
    {
      title: t("Type"),
      dataIndex: "type",
      key: "type",
      filteredValue: filteredInfo.type ?? null,
      filters: [
        {
          value: "0",
          text: "System",
        },
        {
          value: "1",
          text: "Custom",
        },
      ],
      onFilter: (value, record) => Number(record.type) === Number(value),
      render: (_, record) => getLabelTypeTextByNumber(record.type),
    },
    {
      title: t("Action"),
      key: "action",
      width: 100,
      render: (_, record) => (
        <Space>
          <EditLabelButton label={record} />
          <DeleteLabelButton label={record} />
        </Space>
      ),
    },
  ]

  return (
    <>
      <Space style={{ marginBottom: 16, display: "flex", justifyContent: "right" }}>
        <Button id="clear-filters-and-sorters" onClick={clearAll}>
          {t("Clear filters and sorters")}
        </Button>
      </Space>
      <Table
        loading={isFetching}
        dataSource={labels}
        columns={columns}
        rowKey="id"
        style={{ marginTop: 12 }}
        onChange={handleChange}
        id="administration-projects-labels"
        rowClassName="administration-projects-labels-row"
      />
    </>
  )
}
