import { Divider, Space, Typography } from "antd"
import { MeContext } from "processes"
import { useContext, useEffect } from "react"
import { useTranslation } from "react-i18next"

import { ProjectContext } from "pages/project"

import { Field, TagBoolean } from "shared/ui"

import { LayoutView } from "widgets/[ui]"

import { ProjectDetailsActiveTabContext } from "../project-details-main"
import { EditTestResultsSettings } from "./edit-test-results-settings"

export const ProjectDetailsSettingsPage = () => {
  const { t } = useTranslation()
  const { setProjectDetailsActiveTab } = useContext(ProjectDetailsActiveTabContext)!
  useEffect(() => {
    setProjectDetailsActiveTab("settings")
  })
  const { project } = useContext(ProjectContext)!
  const { me } = useContext(MeContext)
  const editable = !project.is_archive || me?.is_superuser

  const editTime = project.settings.result_edit_limit
    ? `${project.settings.result_edit_limit}`
    : `Unlimited`
  return (
    <LayoutView style={{ padding: 24, minHeight: 360 }}>
      {project.is_manageable && editable && (
        <Space style={{ marginBottom: "16px", float: "right" }}>
          <EditTestResultsSettings project={project} />
        </Space>
      )}
      <Divider orientation="left" orientationMargin={0}>
        <div style={{ display: "flex", alignItems: "center", margin: "12px 0" }}>
          <Typography.Title style={{ margin: "0 8px 0 0" }} level={4}>
            {t("Test Results")}
          </Typography.Title>
        </div>
      </Divider>

      <div style={{ padding: 8 }}>
        <Field
          title={t("Is Editable")}
          value={
            <TagBoolean
              value={!!project.settings.is_result_editable}
              trueText={t("Yes")}
              falseText={t("No")}
            />
          }
        />
        {project.settings.is_result_editable && <Field title={t("Edit time")} value={editTime} />}
      </div>
    </LayoutView>
  )
}
