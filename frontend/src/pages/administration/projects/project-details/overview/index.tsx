import { Space, Tag } from "antd"
import { MeContext } from "processes"
import { useContext, useEffect } from "react"
import { LayoutView } from "widgets"

import { ProjectIcon } from "entities/project/ui"

import { ArchiveProject, DeleteProject, EditProject } from "features/project"

import { ProjectDetailsActiveTabContext } from "pages/administration/projects/project-details/project-details-main"
import { ProjectContext } from "pages/project"

import { Field, TagBoolean } from "shared/ui"

export const ProjectFields = ({ project }: { project: Project }) => {
  return (
    <>
      <ProjectIcon icon={project.icon} name={project.name} dataTestId="project-icon" />
      <Field title="Name" value={project?.name} dataTestId="project-name" />
      <Field title="Description" value={project?.description} dataTestId="project-description" />
      <Field
        title="Status"
        value={
          <TagBoolean
            value={!project?.is_archive}
            trueText="ACTIVE"
            falseText="ARCHIVED"
            dataTestid="project-status"
          />
        }
      />
      <Field
        title="Private"
        value={
          <Tag color="default" data-testid="project-private">
            {project.is_private ? "Yes" : "No"}
          </Tag>
        }
      />
    </>
  )
}

export const ProjectDetailsOverviewPage = () => {
  const { setProjectDetailsActiveTab } = useContext(ProjectDetailsActiveTabContext)!
  const { project } = useContext(ProjectContext)!
  const { me } = useContext(MeContext)
  const editable = !project.is_archive || me?.is_superuser

  useEffect(() => {
    setProjectDetailsActiveTab("overview")
  })

  return (
    <LayoutView style={{ padding: 24, minHeight: 360 }}>
      {project.is_manageable && (
        <Space style={{ marginBottom: "16px", float: "right" }}>
          {editable && <EditProject project={project} />}
          {project.is_archive ? (
            <DeleteProject project={project} />
          ) : (
            <ArchiveProject project={project} />
          )}
        </Space>
      )}
      <ProjectFields project={project} />
    </LayoutView>
  )
}
