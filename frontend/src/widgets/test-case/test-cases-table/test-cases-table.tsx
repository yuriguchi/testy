import { Table } from "antd"
import { memo } from "react"

import { useTestCasesTable } from "./use-test-cases-table"

export const TestCasesTable = memo(() => {
  const {
    data,
    columns,
    isLoading,
    selectedTestCase,
    paginationTable,
    handleTableChange,
    handleRowClick,
  } = useTestCasesTable()

  return (
    <Table
      loading={isLoading}
      rowKey="id"
      rowClassName={(record) => (record.id === selectedTestCase?.id ? "active" : "")}
      style={{ cursor: "pointer" }}
      columns={columns}
      dataSource={data}
      size="small"
      pagination={paginationTable}
      onChange={handleTableChange}
      onRow={(record) => {
        return {
          onClick: () => handleRowClick(record),
        }
      }}
    />
  )
})

TestCasesTable.displayName = "TestCasesTable"
