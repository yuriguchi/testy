import { useContext } from "react"
import { useTranslation } from "react-i18next"

import { ProjectStats } from "entities/project/ui"

import { FolowProject } from "features/project"

import { ArchivedTag } from "shared/ui"

import { ProjectTestsProgressBlock } from "widgets/project/ui"

import { ProjectContext } from "../project-layout"
import styles from "./styles.module.css"

export const ProjectOverviewPage = () => {
  const { t } = useTranslation()
  const { project } = useContext(ProjectContext)!

  return (
    <div className={styles.wrapper}>
      <div className={styles.headerContainer}>
        <div className={styles.header}>
          <div className={styles.projectTitle}>
            {project.is_archive && <ArchivedTag size="lg" />}
            <span>{project.name}</span>
          </div>
          <span className={styles.overview}>{t("Overview")}</span>
        </div>
        <div className={styles.actions}>
          <FolowProject project={project} />
        </div>
      </div>
      <ProjectStats
        testSuites={project.suites_count}
        testCases={project.cases_count}
        testPlans={project.plans_count}
        tests={project.tests_count}
      />
      <ProjectTestsProgressBlock />
    </div>
  )
}
