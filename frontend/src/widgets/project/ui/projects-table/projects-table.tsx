import { Button, Flex, Table } from "antd"
import cn from "classnames"
import { useTranslation } from "react-i18next"

import { Toggle } from "shared/ui"

import { useProjectsTable } from "../../model/use-projects-table"
import styles from "./styles.module.css"

export const ProjectsTable = () => {
  const { t } = useTranslation()
  const {
    isLoading,
    isShowArchive,
    columns,
    projects,
    paginationTable,
    handleClearAll,
    handleChange,
    handleRowClick,
    handleShowArchive,
  } = useProjectsTable()

  return (
    <>
      <Flex
        vertical
        gap={16}
        align="flex-end"
        style={{
          marginBottom: 16,
          float: "right",
        }}
      >
        <Button id="clear-filters-and-sorters" onClick={handleClearAll}>
          {t("Clear filters and sorters")}
        </Button>
        <Toggle
          id="test-cases-archive-toggle"
          label={t("Show Archived")}
          checked={isShowArchive}
          size="lg"
          onChange={handleShowArchive}
        />
      </Flex>
      <Table
        dataSource={projects?.results ?? []}
        columns={columns}
        loading={isLoading}
        rowKey="id"
        style={{ marginTop: 12, cursor: "pointer" }}
        onChange={handleChange}
        pagination={paginationTable}
        rowClassName={(record) => {
          return cn({
            [styles.disabledRow]: record.is_private && !record.is_manageable,
          })
        }}
        onRow={(record) => {
          return {
            onClick: () => handleRowClick(record),
          }
        }}
      />
    </>
  )
}
