import { Select } from "antd"
import { useStatuses } from "entities/status/model/use-statuses"
import { useContext, useState } from "react"
import { useTranslation } from "react-i18next"

import { ProjectContext } from "pages/project"

import { Status } from "shared/ui"
import { UntestedStatus } from "shared/ui/status"

import styles from "./styles.module.css"

interface Props extends HTMLDataAttribute {
  value: string[]
  onChange: (value: string[]) => void
  onClose?: () => void
  onClear?: () => void
}

export const StatusFilter = ({ value, onChange, onClose, onClear, ...props }: Props) => {
  const { t } = useTranslation()

  const { project } = useContext(ProjectContext)!
  const { statuses, isLoading } = useStatuses({ project: project.id })
  const [isOpen, setIsOpen] = useState(false)

  const handleChange = (dataValue: string[]) => {
    if (!dataValue.length) {
      onClear?.()
      return
    }

    onChange(dataValue)
  }

  const handleDropdownVisibleChange = (toggle: boolean) => {
    setIsOpen(toggle)
    if (!toggle) {
      onClose?.()
    }
  }

  return (
    <Select
      placeholder={t("Filter by Status")}
      mode="multiple"
      showSearch
      style={{ width: "100%" }}
      loading={isLoading}
      allowClear
      className={styles.select}
      value={isLoading ? [] : value}
      onChange={handleChange}
      onClear={onClear}
      open={isOpen}
      onDropdownVisibleChange={handleDropdownVisibleChange}
      {...props}
    >
      <Select.Option key="untested" value="null" data-testid="status-filter-untested">
        <UntestedStatus />
      </Select.Option>
      {statuses.map((status) => (
        <Select.Option
          key={status.id}
          value={String(status.id)}
          data-testid={`status-filter-status-${status.name}`}
        >
          <Status id={status.id} name={status.name} color={status.color} />
        </Select.Option>
      ))}
    </Select>
  )
}
