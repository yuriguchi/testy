import { PageHeader } from "@ant-design/pro-layout"
import { Breadcrumb, Layout, Space } from "antd"
import { useTranslation } from "react-i18next"
import { LayoutView } from "widgets"

import { CreateProject } from "features/project"

import { ProjectsTable } from "widgets/project/ui/projects-table/projects-table"

const { Content } = Layout

export const ProjectsMain = () => {
  const { t } = useTranslation()
  const breadcrumbItems = [
    <Breadcrumb.Item key="administration">{t("Administration")}</Breadcrumb.Item>,
    <Breadcrumb.Item key="projects">{t("Projects")}</Breadcrumb.Item>,
  ]

  return (
    <>
      <PageHeader
        breadcrumbRender={() => <Breadcrumb>{breadcrumbItems}</Breadcrumb>}
        title={t("Projects")}
        ghost={false}
        style={{ paddingBottom: 0 }}
      />
      <Content style={{ margin: "24px" }}>
        <LayoutView style={{ padding: 24, minHeight: 360 }}>
          <Space style={{ marginBottom: "16px", display: "flex", justifyContent: "right" }}>
            <CreateProject />
          </Space>
          <ProjectsTable />
        </LayoutView>
      </Content>
    </>
  )
}
