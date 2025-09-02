import { Layout } from "antd"

import { DashboardView } from "widgets/dashboard"

const { Content } = Layout

export const DashboardPage = () => {
  return (
    <Content
      style={{ margin: "20px 32px", marginTop: 0, display: "flex", flexDirection: "column" }}
    >
      <DashboardView />
    </Content>
  )
}
