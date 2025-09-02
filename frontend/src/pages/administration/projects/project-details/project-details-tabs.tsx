import { Tabs } from "antd"
import { useContext } from "react"
import { useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"

import { ProjectDetailsActiveTabContext } from "./project-details-main"

interface ProjectDetailsTabsProps {
  projectId: number
  showAccessManagement?: boolean
}

const ProjectDetailsTabs = ({
  projectId,
  showAccessManagement = true,
}: ProjectDetailsTabsProps) => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { projectDetailsActiveTab } = useContext(ProjectDetailsActiveTabContext)!

  const tabItems = [
    {
      label: t("Overview"),
      key: "overview",
      path: `/administration/projects/${projectId}/overview`,
    },
    {
      label: t("Parameters"),
      key: "parameters",
      path: `/administration/projects/${projectId}/parameters`,
    },
    {
      label: t("Labels"),
      key: "labels",
      path: `/administration/projects/${projectId}/labels`,
    },
    {
      label: t("Statuses"),
      key: "statuses",
      path: `/administration/projects/${projectId}/statuses`,
    },
    {
      label: t("Custom Attributes"),
      key: "attributes",
      path: `/administration/projects/${projectId}/attributes`,
    },
    {
      label: t("Settings"),
      key: "settings",
      path: `/administration/projects/${projectId}/settings`,
    },
  ]

  if (showAccessManagement) {
    tabItems.push({
      label: t("Access Management"),
      key: "access-management",
      path: `/administration/projects/${projectId}/access-management`,
    })
  }

  const onChange = (key: string) => {
    const activeTabItem = tabItems.find((i) => i.key === key)
    if (!activeTabItem) return
    navigate(activeTabItem.path)
  }

  return <Tabs activeKey={projectDetailsActiveTab} items={tabItems} onChange={onChange} />
}

export default ProjectDetailsTabs
