import { Card } from "antd"
import { Content } from "antd/es/layout/layout"
import { useContext, useEffect } from "react"
import { useTranslation } from "react-i18next"
import { NotificationSettingsTable } from "widgets"

import { NotificationsActiveTabContext } from "./notifications-page"

export const NotificationSettingsPage = () => {
  const { t } = useTranslation()
  const { setActiveTab, setTitle } = useContext(NotificationsActiveTabContext)!

  useEffect(() => {
    setActiveTab("settings")
    setTitle(t("Notification settings"))
  }, [])

  return (
    <Card>
      <Content>
        <NotificationSettingsTable />
      </Content>
    </Card>
  )
}
