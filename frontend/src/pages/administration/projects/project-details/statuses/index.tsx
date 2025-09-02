import { CheckOutlined } from "@ant-design/icons"
import { Button, Space, notification } from "antd"
import { useContext, useEffect, useState } from "react"
import { useTranslation } from "react-i18next"
import { LayoutView, StatusesTable } from "widgets"

import { useUpdateProjectJsonMutation } from "entities/project/api"

import { CreateStatusButton } from "features/status"

import { ProjectContext } from "pages/project"

import { initInternalError } from "shared/libs"
import { AlertSuccessChange } from "shared/ui"

import { ProjectDetailsActiveTabContext } from "../project-details-main"

export const ProjectDetailsStatusesPage = () => {
  const { t } = useTranslation()
  const { project } = useContext(ProjectContext)!
  const { setProjectDetailsActiveTab } = useContext(ProjectDetailsActiveTabContext)!
  const [orderedStatuses, setOrderedStatuses] = useState<Status[]>([])
  const [updateProject] = useUpdateProjectJsonMutation()

  useEffect(() => {
    setProjectDetailsActiveTab("statuses")
  }, [])

  const handleChangeOrder = (statuses: Status[]) => {
    setOrderedStatuses(statuses)
  }

  const handleSaveOrder = async () => {
    try {
      const status_order = orderedStatuses.reduce(
        (acc, status, index) => {
          acc[status.id] = index
          return acc
        },
        {} as Record<string, number>
      )

      await updateProject({
        id: project.id,
        body: { settings: { status_order } },
      }).unwrap()

      notification.success({
        message: t("Success"),
        description: (
          <AlertSuccessChange
            action="updated"
            title={t("Project status settings")}
            link={`/administration/projects/${project.id}/statuses`}
            id={String(project.id)}
          />
        ),
      })

      setOrderedStatuses([])
    } catch (err) {
      initInternalError(err)
    }
  }

  return (
    <LayoutView style={{ padding: 24, minHeight: 360 }}>
      <Space style={{ display: "flex", justifyContent: "right" }}>
        <CreateStatusButton />
        <Button
          id="save-order"
          type="primary"
          icon={<CheckOutlined />}
          onClick={handleSaveOrder}
          style={{ marginBottom: 16, float: "right" }}
          disabled={!orderedStatuses.length}
        >
          {t("Save order")}
        </Button>
      </Space>
      <StatusesTable onChangeOrder={handleChangeOrder} />
    </LayoutView>
  )
}
