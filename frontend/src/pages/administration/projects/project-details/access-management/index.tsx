import { Space } from "antd"
import { useContext, useEffect } from "react"
import { LayoutView } from "widgets"

import { ProjectDetailsActiveTabContext } from "pages/administration/projects/project-details/project-details-main"
import { ProjectContext } from "pages/project"

import { AddUserProjectAccess } from "widgets/user/user-project-access-modal/add-user-project-access"
import { UserProjectAccessModal } from "widgets/user/user-project-access-modal/user-project-access-modal"
import { UsersProjectAccessTable } from "widgets/user/users-project-access-table/users-project-access-table"

export const ProjectDetailsAccessManagementPage = () => {
  const { setProjectDetailsActiveTab } = useContext(ProjectDetailsActiveTabContext)!
  const { project } = useContext(ProjectContext)!

  useEffect(() => {
    setProjectDetailsActiveTab("access-management")
  }, [])

  return (
    <LayoutView style={{ padding: 24, minHeight: 360 }}>
      <Space style={{ display: "flex", justifyContent: "right" }}>
        {project.is_manageable && <AddUserProjectAccess />}
      </Space>
      <UsersProjectAccessTable isManageable={project.is_manageable} />
      <UserProjectAccessModal />
    </LayoutView>
  )
}
