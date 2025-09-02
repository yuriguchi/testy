import { Fragment, memo, useContext, useMemo } from "react"
import { useNavigate } from "react-router-dom"
import { Link } from "react-router-dom"

import { useGetBreadcrumbsQuery as useGetSuitesBreadcrumbsQuery } from "entities/suite/api"

import { useGetBreadcrumbsQuery as useGetPlansBreadcrumbsQuery } from "entities/test-plan/api"

import { ProjectContext } from "pages/project/project-layout"

import { icons } from "shared/assets/inner-icons"

import styles from "./styles.module.css"

const { ArrowIcon } = icons

const formatToArray = (
  breadcrumbs: EntityBreadcrumbs,
  arr: { id: number; title: string; parent: EntityBreadcrumbs | null }[]
) => {
  arr.push(breadcrumbs)
  if (breadcrumbs.parent) {
    formatToArray(breadcrumbs.parent, arr)
  }
  return arr
}

interface Props {
  activeTab: "suites" | "plans"
  entityId?: number | string
}

export const TreebarBreadcrumbs = memo(({ activeTab, entityId }: Props) => {
  const { project } = useContext(ProjectContext)!
  const navigate = useNavigate()

  const { data: dataSuites } = useGetSuitesBreadcrumbsQuery(Number(entityId), {
    skip: activeTab !== "suites" || !entityId,
  })
  const { data: dataPlans } = useGetPlansBreadcrumbsQuery(Number(entityId), {
    skip: activeTab !== "plans" || !entityId,
  })
  const data = activeTab === "suites" ? dataSuites : dataPlans

  const breadcrumbs = useMemo(() => {
    if (!entityId) {
      return []
    }

    return data ? formatToArray(data, []).reverse() : []
  }, [data, entityId])

  const activeBreadcrumb = breadcrumbs.find((i) => String(i.id) === entityId)

  return (
    <div className={styles.breadcrumbsBlock} data-testid="treebar-breadcrumbs-block">
      <div className={styles.breadcrumbsIcons}>
        {!!breadcrumbs.length && (
          <ArrowIcon
            className={styles.breadCrumbsArrowIcon}
            onClick={(e) => {
              // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
              e.stopPropagation()

              const link = activeBreadcrumb?.parent
                ? `${activeBreadcrumb?.parent?.id}?rootId=${activeBreadcrumb?.parent?.id}`
                : ""

              navigate(`/projects/${project.id}/${activeTab}/${link}`)
            }}
            data-testid="treebar-breadcrumbs-back"
          />
        )}
      </div>
      <Link
        to={`/projects/${project.id}/${activeTab}/`}
        className={styles.breadcrumbsTitle}
        data-testid="treebar-breadcrumbs-home"
      >
        HOME
      </Link>
      {breadcrumbs.map((breadcrumb) => (
        <Fragment key={breadcrumb.id}>
          <span className={styles.breadcrumbsDiv}>/</span>
          <Link
            to={`/projects/${project.id}/${activeTab}/${breadcrumb.id}?rootId=${breadcrumb.id}`}
            key={breadcrumb.id}
            className={styles.breadcrumbsTitle}
            data-testid={`treebar-breadcrumbs-title-${breadcrumb.title}`}
          >
            {breadcrumb.title}
          </Link>
        </Fragment>
      ))}
    </div>
  )
})

TreebarBreadcrumbs.displayName = "TreebarBreadcrumbs"
