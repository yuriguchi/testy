import { Table } from "antd"

import { useProjectsDashboardTable } from "widgets/project/model"

interface Props {
  searchName: string
}

export const ProjectsDashboardTable = ({ searchName }: Props) => {
  const { isLoading, columns, projects, paginationTable, handleChange } = useProjectsDashboardTable(
    { searchName }
  )

  return (
    <Table
      loading={isLoading}
      dataSource={projects?.results ?? []}
      columns={columns}
      rowKey="id"
      onChange={handleChange}
      pagination={paginationTable}
    />
  )
}
