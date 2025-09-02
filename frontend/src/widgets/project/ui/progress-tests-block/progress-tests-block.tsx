import { Typography } from "antd"
import Table from "antd/lib/table"
import { useTranslation } from "react-i18next"

import { useProjectOverviewProgress } from "widgets/project/model/use-project-overview-progress"

import styles from "./styles.module.css"

export const ProjectTestsProgressBlock = () => {
  const { t } = useTranslation()
  const { columns, data, isLoading } = useProjectOverviewProgress()

  return (
    <div className={styles.wrapper}>
      <div className={styles.header}>
        <Typography.Title level={4}>{t("Executed tests progress")}</Typography.Title>
      </div>
      <Table
        dataSource={data}
        columns={columns}
        rowKey="id"
        className={styles.table}
        pagination={{
          defaultPageSize: 5,
        }}
        id="projects-overview-table"
        loading={isLoading}
      />
    </div>
  )
}
