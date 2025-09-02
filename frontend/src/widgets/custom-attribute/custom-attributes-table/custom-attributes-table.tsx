import { Button, Space, Table, TableProps } from "antd"
import { ColumnsType } from "antd/es/table"
import type { FilterValue, TablePaginationConfig } from "antd/es/table/interface"
import { useGetCustomAttributesQuery } from "entities/custom-attribute/api"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { useParams } from "react-router-dom"

import { ChangeCustomAttribute, DeleteCustomAttribute } from "features/custom-attribute"

import { customAttributeTypes, customAttributesObject } from "shared/config/custom-attribute-types"
import { useTableSearch } from "shared/hooks"

export const CustomAttributesTable = () => {
  const { t } = useTranslation()
  const { projectId } = useParams<ParamProjectId>()

  const { data, isFetching } = useGetCustomAttributesQuery({ project: projectId ?? "" })

  const [filteredInfo, setFilteredInfo] = useState<Record<string, FilterValue | null>>({})
  const { setSearchText, getColumnSearch } = useTableSearch()

  const handleChange: TableProps<CustomAttribute>["onChange"] = (
    pagination: TablePaginationConfig,
    filters: Record<string, FilterValue | null>
  ) => {
    setFilteredInfo(filters)
  }

  const clearAll = () => {
    setFilteredInfo({})
    setSearchText("")
  }

  const columns: ColumnsType<CustomAttribute> = [
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
      filters: customAttributeTypes.map(({ value, label }) => ({ value, text: label })),
      onFilter: (value, record) => record.type === value,
      render: (_, record) => <Space>{customAttributesObject[record.type]}</Space>,
    },
    {
      title: t("Applied To"),
      dataIndex: "applied_to",
      key: "applied_to",
      render: (value) => {
        return <Space>{Object.keys(value as object).join(", ")}</Space>
      },
    },
    {
      title: t("Action"),
      key: "action",
      width: 100,
      render: (_, record) => (
        <Space>
          <ChangeCustomAttribute formType="edit" attribute={record} />
          <DeleteCustomAttribute attributeId={record.id} />
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
        dataSource={data}
        columns={columns}
        rowKey="id"
        style={{ marginTop: 12 }}
        onChange={handleChange}
        id="administration-projects-attributes"
        rowClassName="administration-projects-attributes-row"
      />
    </>
  )
}
