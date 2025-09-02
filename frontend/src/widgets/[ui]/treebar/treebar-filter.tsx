import { Divider, Flex, Radio, Space, Typography } from "antd"
import { TreebarContext } from "processes"
import { useContext } from "react"
import { useTranslation } from "react-i18next"

import { Toggle } from "shared/ui"

interface Props {
  activeTab: "plans" | "suites"
}

export const TreebarFilter = ({ activeTab }: Props) => {
  const { t } = useTranslation()
  const { treeSettings, updateTreeSettings } = useContext(TreebarContext)!

  const BASE_PLANS_FILTER_OPTIONS = [
    { value: "name", label: t("Name") },
    { value: "started_at", label: t("Start Date") },
    { value: "created_at", label: t("Created At") },
  ]
  const BASE_SUITES_FILTER_OPTIONS = [
    { value: "name", label: t("Name") },
    { value: "created_at", label: t("Created At") },
  ]

  const FILTER_OPTIONS =
    activeTab === "plans" ? BASE_PLANS_FILTER_OPTIONS : BASE_SUITES_FILTER_OPTIONS

  const handleSortBy = (sort: "asc" | "desc") => {
    updateTreeSettings({ [activeTab]: { ...treeSettings[activeTab], sortBy: sort } })
  }

  const handleFilterBy = (field: string) => {
    updateTreeSettings({ [activeTab]: { ...treeSettings[activeTab], filterBy: field } })
  }

  const handleShowArchived = () => {
    updateTreeSettings({ show_archived: !treeSettings.show_archived })
  }

  return (
    <Flex gap={8} vertical style={{ minWidth: 200 }} data-testid="treebar-filter-container">
      <Divider orientation="left" style={{ margin: 0 }} orientationMargin={0}>
        <Typography.Text type="secondary">{t("Sort by")}</Typography.Text>
      </Divider>
      <Radio.Group
        onChange={(value) => {
          handleFilterBy(value.target.value as string)
        }}
        value={treeSettings[activeTab].filterBy}
        defaultValue={FILTER_OPTIONS[0].value}
        data-testid="treebar-filter-group"
      >
        <Space direction="vertical">
          {FILTER_OPTIONS.map((option, index) => (
            <Radio key={index} value={option.value} data-testid={`treebar-filter-${option.value}`}>
              {option.label}
            </Radio>
          ))}
        </Space>
      </Radio.Group>
      <Divider style={{ margin: "4px 0" }} />
      <Radio.Group
        onChange={(value) => {
          handleSortBy(value.target.value as "asc" | "desc")
        }}
        value={treeSettings[activeTab].sortBy}
        data-testid="treebar-filter-sort-by-group"
      >
        <Space direction="vertical">
          <Radio value="asc" data-testid="treebar-filter-ascending">
            {t("Ascending")}
          </Radio>
          <Radio value="desc" data-testid="treebar-filter-descending">
            {t("Descending")}
          </Radio>
        </Space>
      </Radio.Group>
      {activeTab === "plans" && (
        <>
          <Divider style={{ margin: "4px 0" }} />
          <Toggle
            id="archive-toggle"
            label={t("Show Archived")}
            checked={treeSettings.show_archived}
            onChange={handleShowArchived}
          />
        </>
      )}
    </Flex>
  )
}
