import { PlusOutlined } from "@ant-design/icons"
import { Button, Space } from "antd"
import { useContext, useEffect } from "react"
import { useTranslation } from "react-i18next"
import { useDispatch } from "react-redux"
import { useOutletContext } from "react-router-dom"
import { LayoutView } from "widgets"

import { showCreateParameterModal } from "entities/parameter/model"
import { ParametersTable } from "entities/parameter/ui/parameters-table"

import { ProjectDetailsActiveTabContext } from "pages/administration/projects/project-details/project-details-main"

import { CreateEditParameterModal } from "./create-edit-parameter-modal"

export const ProjectDetailsParametersPage = () => {
  const { t } = useTranslation()
  const dispatch = useDispatch()
  const { setProjectDetailsActiveTab } = useContext(ProjectDetailsActiveTabContext)!
  const projectId: Id = useOutletContext()

  useEffect(() => {
    setProjectDetailsActiveTab("parameters")
  }, [])

  const handleCreateClick = () => {
    dispatch(showCreateParameterModal())
  }

  return (
    <LayoutView style={{ padding: 24, minHeight: 360 }}>
      <Space style={{ display: "flex", justifyContent: "right" }}>
        <Button
          id="create-parameter"
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleCreateClick}
          style={{ marginBottom: 16, float: "right" }}
        >
          {t("Create")} {t("Parameter")}
        </Button>
      </Space>
      <CreateEditParameterModal projectId={projectId} />
      <ParametersTable />
    </LayoutView>
  )
}
