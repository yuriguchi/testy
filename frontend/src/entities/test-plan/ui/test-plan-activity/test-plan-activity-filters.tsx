import { Button, Space, Table, Typography } from "antd"
import { useTranslation } from "react-i18next"

import { useTestPlanActivity, useTestPlanActivityFilters } from "entities/test-plan/model"

export const TestPlanActivityFilers = ({
  testPlanActivity,
}: {
  testPlanActivity: ReturnType<typeof useTestPlanActivity>
}) => {
  const { t } = useTranslation()
  const { filters, handleChange } = useTestPlanActivityFilters(testPlanActivity)

  return (
    <div
      style={{ display: "flex", marginBottom: 48, flexDirection: "column" }}
      data-testid="test-plan-activity-filters"
    >
      <div
        style={{
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: 14,
        }}
      >
        <Typography.Paragraph strong style={{ marginBottom: 0 }}>
          {t("Common Filters")}
        </Typography.Paragraph>

        <Space style={{ display: "flex", justifyContent: "right" }}>
          <Button id="clear-filters-and-sorters" onClick={testPlanActivity.clearFilters}>
            {t("Clear filters and sorters")}
          </Button>
        </Space>
      </div>
      <Table
        columns={filters}
        dataSource={[]}
        rowKey="id"
        pagination={false}
        loading={false}
        className="test-plan-activity-filters"
        onChange={handleChange}
      />
    </div>
  )
}
