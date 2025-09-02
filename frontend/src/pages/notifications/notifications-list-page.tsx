import { Card } from "antd"
import { Content } from "antd/es/layout/layout"
import { useContext, useEffect } from "react"
import { useTranslation } from "react-i18next"

import { NotificationsTable } from "widgets/notifications/notifications-table/notifications-table"

import { NotificationsActiveTabContext } from "./notifications-page"

export const NotificationListPage = () => {
  const { t } = useTranslation()
  const { setActiveTab, setTitle } = useContext(NotificationsActiveTabContext)!

  useEffect(() => {
    setActiveTab("overview")
    setTitle(t("Notifications"))
  }, [])

  return (
    <Card>
      <Content>
        <NotificationsTable />
      </Content>
    </Card>
  )
}
