import React, { useContext } from "react"
import { Outlet, useParams } from "react-router-dom"

import { useGetProjectQuery } from "entities/project/api"

export interface ProjectContextType {
  project: Project
}

export const ProjectContext = React.createContext<ProjectContextType | null>(null)

export const ProjectLayout = () => {
  const { projectId } = useParams<ParamProjectId>()
  const { data: project } = useGetProjectQuery(Number(projectId), {
    skip: !projectId,
  })

  if (!project) return null

  return (
    <ProjectContext.Provider value={{ project }}>
      <Outlet context={projectId} />
    </ProjectContext.Provider>
  )
}

export const useProjectContext = () => {
  const { project } = useContext(ProjectContext)!
  return project
}
