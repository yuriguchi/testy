import { Button, Flex, Tooltip } from "antd"
import { useTranslation } from "react-i18next"

import TreeIcon from "shared/assets/icons/tree-view.svg?react"
import { icons } from "shared/assets/inner-icons"

const { TableIcon } = icons

interface Props<T> {
  value: T
  onChange: (value: T) => void
}

// eslint-disable-next-line comma-spacing
export const DataViewSelect = <T,>({ value, onChange }: Props<T>) => {
  const { t } = useTranslation()

  return (
    <Flex gap={8} data-testid="data-view-select">
      <Tooltip title={t("Table view")} placement="topLeft">
        <Button
          ghost={value !== "list"}
          onClick={() => onChange("list" as T)}
          icon={<TableIcon color="var(--y-sky-40)" />}
          data-testid="data-view-select-table"
        />
      </Tooltip>
      <Tooltip title={t("Tree view")} placement="topLeft">
        <Button
          ghost={value !== "tree"}
          onClick={() => onChange("tree" as T)}
          icon={<TreeIcon color="var(--y-sky-40)" width={18} height={18} />}
          data-testid="data-view-select-tree"
        />
      </Tooltip>
    </Flex>
  )
}
