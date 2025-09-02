import { DeleteOutlined, EditOutlined } from "@ant-design/icons"
import { Button, Modal, Space, Table, TableProps, notification } from "antd"
import { ColumnsType } from "antd/es/table"
import type { FilterValue, TablePaginationConfig } from "antd/es/table/interface"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { useDispatch } from "react-redux"
import { useParams } from "react-router-dom"

import { useDeleteParameterMutation, useGetParametersQuery } from "entities/parameter/api"
import { setParameter, showEditParameterModal } from "entities/parameter/model"

import { useTableSearch } from "shared/hooks"
import { initInternalError } from "shared/libs"

export const ParametersTable = () => {
  const { t } = useTranslation()
  const dispatch = useDispatch()
  const { projectId } = useParams<ParamProjectId>()
  const { data: parameters, isFetching } = useGetParametersQuery(Number(projectId), {
    skip: !projectId,
  })
  const [deleteParameter] = useDeleteParameterMutation()

  const [filteredInfo, setFilteredInfo] = useState<Record<string, FilterValue | null>>({})
  const { setSearchText, getColumnSearch } = useTableSearch()

  const showParameterDetail = (parameter: IParameter) => {
    dispatch(setParameter(parameter))
    dispatch(showEditParameterModal())
  }

  const handleChange: TableProps<IParameter>["onChange"] = (
    pagination: TablePaginationConfig,
    filters: Record<string, FilterValue | null>
  ) => {
    setFilteredInfo(filters)
  }

  const clearAll = () => {
    setFilteredInfo({})
    setSearchText("")
  }

  const columns: ColumnsType<IParameter> = [
    {
      title: t("Name"),
      dataIndex: "data",
      key: "data",
      filteredValue: filteredInfo.data ?? null,
      ...getColumnSearch("data"),
      onFilter: (value, record) => record.data.toLowerCase().includes(String(value).toLowerCase()),
      render: (value, record) => <span data-testid={`${record.data}-name`}>{value}</span>,
    },
    {
      title: t("Group"),
      dataIndex: "group_name",
      key: "group_name",
      filteredValue: filteredInfo.group_name ?? null,
      ...getColumnSearch("group_name"),
      onFilter: (value, record) =>
        record.group_name.toLowerCase().includes(String(value).toLowerCase()),
      render: (value, record) => <span data-testid={`${record.data}-group-name`}>{value}</span>,
    },
    {
      title: t("Action"),
      key: "action",
      width: 100,
      render: (_, record) => (
        <Space>
          <Button
            id={`${record.data}-edit`}
            icon={<EditOutlined />}
            shape="circle"
            onClick={() => showParameterDetail(record)}
          />
          <Button
            id={`${record.data}-delete`}
            icon={<DeleteOutlined />}
            shape="circle"
            danger
            onClick={() => {
              Modal.confirm({
                title: t("Do you want to delete these parameter?"),
                okText: t("Delete"),
                cancelText: t("Cancel"),
                onOk: async () => {
                  try {
                    await deleteParameter(record.id).unwrap()
                    notification.success({
                      message: t("Success"),
                      closable: true,
                      description: t("Parameter deleted successfully"),
                    })
                  } catch (err: unknown) {
                    initInternalError(err)
                  }
                },
                okButtonProps: { "data-testid": "delete-parameter-button-confirm" },
                cancelButtonProps: { "data-testid": "delete-parameter-button-cancel" },
              })
            }}
          />
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
        dataSource={parameters}
        columns={columns}
        rowKey="data"
        style={{ marginTop: 12 }}
        onChange={handleChange}
        id="administration-projects-parameters"
        rowClassName="administration-projects-parameters-row"
      />
    </>
  )
}
