import { Content } from "antd/lib/layout/layout"
import { LayoutView } from "widgets"

import { TestPlanActivityWrapper } from "entities/test-plan/ui"

export const TestPlanActivityPage = () => {
  return (
    <Content>
      <LayoutView style={{ minHeight: 360 }}>
        <TestPlanActivityWrapper />
      </LayoutView>
    </Content>
  )
}
