import { Space } from "antd"
import { useContext, useEffect } from "react"
import { LayoutView } from "widgets"

import { CreateLabelButton } from "features/label"

import { ProjectDetailsActiveTabContext } from "pages/administration/projects/project-details/project-details-main"

import { LabelsTable } from "widgets/label"

export const ProjectDetailsLabelsPage = () => {
  const { setProjectDetailsActiveTab } = useContext(ProjectDetailsActiveTabContext)!

  useEffect(() => {
    setProjectDetailsActiveTab("labels")
  }, [])

  return (
    <LayoutView style={{ padding: 24, minHeight: 360 }}>
      <Space style={{ display: "flex", justifyContent: "right" }}>
        <CreateLabelButton />
      </Space>
      <LabelsTable />
    </LayoutView>
  )
}
