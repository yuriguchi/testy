import { PageHeader } from "@ant-design/pro-layout"
import { Layout } from "antd"
import { createContext, useState } from "react"
import { Outlet } from "react-router-dom"
import { NotificationsTabs } from "widgets"

const { Content } = Layout

export interface NotificationsActiveTabContextType {
  activeTab: string
  setActiveTab: React.Dispatch<React.SetStateAction<string>>
  setTitle: React.Dispatch<React.SetStateAction<string>>
}

export const NotificationsActiveTabContext =
  createContext<NotificationsActiveTabContextType | null>(null)

export const NotificationsPage = () => {
  const [activeTab, setActiveTab] = useState("")
  const [title, setTitle] = useState("")

  return (
    <NotificationsActiveTabContext.Provider
      value={{
        activeTab,
        setActiveTab,
        setTitle,
      }}
    >
      <PageHeader
        title={title}
        ghost={false}
        footer={<NotificationsTabs />}
        style={{ paddingBottom: 0 }}
      ></PageHeader>
      <Content style={{ margin: "24px" }}>
        <Outlet />
      </Content>
    </NotificationsActiveTabContext.Provider>
  )
}
