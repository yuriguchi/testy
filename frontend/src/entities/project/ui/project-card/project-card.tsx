import { Flex } from "antd"
import cn from "classnames"
import { useTranslation } from "react-i18next"
import { Link } from "react-router-dom"

import { RequestProjectAccess } from "features/project"

import { icons } from "shared/assets/inner-icons"
import { createConcatIdsFn } from "shared/libs"
import { ArchivedTag } from "shared/ui"

import { ProjectIcon } from ".."
import styles from "./styles.module.css"

const { DashboardIcon, TestPlansIcon, TestSuitesIcon } = icons

interface Props {
  project: Project
  folowProject: React.ReactNode
}

const ICON_STYLE = { width: 16, marginRight: 4 }

export const ProjectCard = ({ project, folowProject }: Props) => {
  const { t } = useTranslation()

  const getIdWithTitle = createConcatIdsFn(project.name)

  return (
    <div className={styles.cardWrapper} data-testid={getIdWithTitle("card-wrapper")}>
      <div className={cn({ [styles.cardBlured]: !project.is_visible })}>
        <div className={cn(styles.cardContainer)}>
          <div className={styles.nameBlock}>
            <ProjectIcon
              icon={project.icon}
              name={project.name}
              size={32}
              dataTestId="project-card-icon"
            />
            <Flex gap={8} align="center">
              {project.is_archive && <ArchivedTag data-testid={getIdWithTitle("archived-tag")} />}
              <Link
                className={styles.name}
                data-testid={getIdWithTitle("name")}
                to={`/projects/${project.id}/overview`}
              >
                {project.name}
              </Link>
            </Flex>
          </div>
          <div className={styles.action} data-testid={getIdWithTitle("action")}>
            {folowProject}
          </div>
          <ul className={styles.dataBlock}>
            <li data-testid={getIdWithTitle("data-block-suites")}>
              <span className={styles.dataCount}>{project.suites_count}</span>
              <span className={styles.dataTitle}>{t("Test Suites")}</span>
            </li>
            <li data-testid={getIdWithTitle("data-block-plans")}>
              <span className={styles.dataCount}>{project.plans_count}</span>
              <span className={styles.dataTitle}>{t("Test Plans")}</span>
            </li>
            <li data-testid={getIdWithTitle("data-block-cases")}>
              <span className={styles.dataCount}>{project.cases_count}</span>
              <span className={styles.dataTitle}>{t("Test Cases")}</span>
            </li>
            <li data-testid={getIdWithTitle("data-block-tests")}>
              <span className={styles.dataCount}>{project.tests_count}</span>
              <span className={styles.dataTitle}>{t("Tests")}</span>
            </li>
          </ul>
        </div>
        <ul className={styles.btnsBlock}>
          <Link id={`${project.name}-link-overview`} to={`/projects/${project.id}/overview`}>
            <li className={styles.btnBlock}>
              <DashboardIcon style={ICON_STYLE} />
              <span className={styles.btnBlockTitle}>{t("Overview")}</span>
            </li>
          </Link>
          <Link id={`${project.name}-link-suites`} to={`/projects/${project.id}/suites`}>
            <li className={styles.btnBlock}>
              <TestSuitesIcon style={ICON_STYLE} />
              <span className={styles.btnBlockTitle}>{t("Test Suites")}</span>
            </li>
          </Link>
          <Link id={`${project.name}-link-plans`} to={`/projects/${project.id}/plans`}>
            <li className={styles.btnBlock}>
              <TestPlansIcon style={ICON_STYLE} />
              <span className={styles.btnBlockTitle}>{t("Test Plans")}</span>
            </li>
          </Link>
        </ul>
      </div>
      {!project.is_visible && <RequestProjectAccess project={project} />}
    </div>
  )
}
