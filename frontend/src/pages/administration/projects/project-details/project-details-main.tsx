import { PageHeader } from "@ant-design/pro-layout"
import { Breadcrumb, Layout } from "antd"
import React, { useContext, useState } from "react"
import { useTranslation } from "react-i18next"
import { Link, Outlet } from "react-router-dom"

import { ProjectContext } from "pages/project"

import ProjectDetailsTabs from "./project-details-tabs"

const { Content } = Layout

export interface ProjectDetailsActiveTabContextType {
  projectDetailsActiveTab: string
  setProjectDetailsActiveTab: React.Dispatch<React.SetStateAction<string>>
}

export const ProjectDetailsActiveTabContext =
  React.createContext<ProjectDetailsActiveTabContextType | null>(null)

export const ProjectDetailsMainPage = () => {
  const { t } = useTranslation()
  const [projectDetailsActiveTab, setProjectDetailsActiveTab] = useState("")
  const { project } = useContext(ProjectContext)!

  const breadcrumbItems = [
    <Breadcrumb.Item key="administration">{t("Administration")}</Breadcrumb.Item>,
    <Breadcrumb.Item key="projects">
      <Link to="/administration/projects">{t("Projects")}</Link>
    </Breadcrumb.Item>,
    <Breadcrumb.Item key={project.id}>{project.name}</Breadcrumb.Item>,
  ]

  return (
    <>
      <ProjectDetailsActiveTabContext.Provider
        value={{ projectDetailsActiveTab, setProjectDetailsActiveTab }}
      >
        <PageHeader
          breadcrumbRender={() => <Breadcrumb>{breadcrumbItems}</Breadcrumb>}
          title={project?.name}
          ghost={false}
          footer={<ProjectDetailsTabs projectId={project.id} />}
          style={{ paddingBottom: 0 }}
        />
        <Content style={{ margin: "24px" }}>
          <Outlet context={project.id} />
        </Content>
      </ProjectDetailsActiveTabContext.Provider>
    </>
  )
}
