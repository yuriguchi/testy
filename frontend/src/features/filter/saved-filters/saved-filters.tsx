import { Select } from "antd"
import { useTranslation } from "react-i18next"

import styles from "./styles.module.css"

interface Props {
  options: string[]
  value: string | null
  onChange: (value: string) => void
}

export const SavedFilters = ({ options, value, onChange }: Props) => {
  const { t } = useTranslation()

  return (
    <Select
      options={options.map((item) => ({ value: item, label: item }))}
      onChange={onChange}
      defaultValue={value}
      value={value ?? t("Saved Filters")}
      rootClassName={styles.selectRoot}
      data-testid="saved-filters-select"
    />
  )
}
