import { Space } from "antd"
import { useContext, useEffect } from "react"
import { LayoutView } from "widgets"

import { ChangeCustomAttribute } from "features/custom-attribute"

import { ProjectDetailsActiveTabContext } from "pages/administration/projects/project-details/project-details-main"

import { CustomAttributesTable } from "widgets/custom-attribute"

export const ProjectDetailsCustomAttributesPage = () => {
  const { setProjectDetailsActiveTab } = useContext(ProjectDetailsActiveTabContext)!

  useEffect(() => {
    setProjectDetailsActiveTab("attributes")
  }, [])

  return (
    <LayoutView style={{ padding: 24, minHeight: 360 }}>
      <Space style={{ display: "flex", justifyContent: "right" }}>
        <ChangeCustomAttribute formType="create" />
      </Space>
      <CustomAttributesTable />
    </LayoutView>
  )
}
