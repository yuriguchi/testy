import { Empty, List } from "antd"

import { ProjectCard, ProjectCardsSkeleton } from "entities/project/ui"

import { FolowProject } from "features/project"

import { useProjectsDashboardCards } from "widgets/project/model/use-projects-dashboard-cards"

import styles from "./styles.module.css"

interface Props {
  searchName: string
}

export const ProjectsDashboardCards = ({ searchName }: Props) => {
  const { isLoading, isLastPage, projects, bottomRef } = useProjectsDashboardCards({ searchName })

  return (
    <div className={styles.wrapper}>
      {!isLoading && !projects.length && <Empty />}
      <div className={styles.list}>
        {projects.map((project) => (
          <List.Item key={project.id} id={`${project.name}-project-card`} style={{ width: "100%" }}>
            <ProjectCard project={project} folowProject={<FolowProject project={project} />} />
          </List.Item>
        ))}
        {isLoading && <ProjectCardsSkeleton />}
        {!isLoading && !!projects.length && !isLastPage && (
          <div id="scroll-pagination-trigger-dashboard" ref={bottomRef} key="trigger" />
        )}
      </div>
    </div>
  )
}
