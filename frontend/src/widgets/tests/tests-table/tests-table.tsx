import { Table } from "antd"
import { memo } from "react"

import { useTestsTable } from "./use-tests-table"

interface Props {
  testPlanId?: number
}

export const TestsTable = memo(({ testPlanId }: Props) => {
  const {
    activeTestId,
    data,
    isLoading,
    paginationTable,
    columns,
    selectedRows,
    handleTableChange,
    handleRowClick,
    handleSelectRows,
  } = useTestsTable({ testPlanId: testPlanId ? Number(testPlanId) : null })

  return (
    <Table
      style={{ cursor: "pointer" }}
      rowClassName={(record) => (record.id === activeTestId ? "active" : "")}
      columns={columns}
      pagination={paginationTable}
      dataSource={data}
      loading={isLoading}
      size="small"
      onChange={handleTableChange}
      onRow={(record) => {
        return {
          onClick: () => handleRowClick(record),
        }
      }}
      rowSelection={{
        selectedRowKeys: selectedRows,
        onChange: handleSelectRows,
        preserveSelectedRowKeys: true,
      }}
      rowKey="id"
    />
  )
})

TestsTable.displayName = "TestsTable"
