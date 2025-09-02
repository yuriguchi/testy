import { TableOutlined } from "@ant-design/icons"
import { Button, Checkbox, Divider, Popover, Tooltip, Typography } from "antd"
import { CheckboxOptionType } from "antd/lib"
import { memo } from "react"
import { useTranslation } from "react-i18next"

interface Props {
  id: string
  columns: ColumnParam[]
  visibilityColumns: ColumnParam[]
  onChange: (data: ColumnParam[]) => void
}

interface CheckboxOption {
  label: string
  value: string
}

const SettingsColumnVisibilityComponent = ({ columns, id, visibilityColumns, onChange }: Props) => {
  const { t } = useTranslation()

  const handleChange = (data: string[]) => {
    const result = columns.filter((i) => data.includes(i.key))
    onChange?.(result)
  }

  const options: CheckboxOption[] = columns.map((i) => ({
    // @ts-ignore
    label: t(i.title),
    value: i.key,
  }))

  return (
    <Popover
      content={
        <Checkbox.Group
          options={options as unknown as CheckboxOptionType<string>[]}
          value={visibilityColumns.map((i) => i.key)}
          onChange={handleChange}
          data-testid="settings-column-visibility-popover"
        />
      }
      title={
        <Divider orientation="left" style={{ margin: 0 }} orientationMargin={0}>
          <Typography.Text type="secondary">{t("Shown columns")}</Typography.Text>
        </Divider>
      }
      trigger="click"
      placement="bottomRight"
    >
      <Tooltip title={t("Shown columns")}>
        <Button id={id} icon={<TableOutlined style={{ color: "var(--y-sky-60)" }} />} />
      </Tooltip>
    </Popover>
  )
}

export const SettingsColumnVisibility = memo(SettingsColumnVisibilityComponent)
