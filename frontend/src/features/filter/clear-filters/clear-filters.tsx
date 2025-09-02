import { Button } from "antd"
import { useTranslation } from "react-i18next"

import { icons } from "shared/assets/inner-icons"

import styles from "./styles.module.css"

const { ResetIcon } = icons

interface Props {
  isVisible: boolean
  onClear: () => void
}

export const ClearFilters = ({ isVisible, onClear }: Props) => {
  const { t } = useTranslation()

  if (!isVisible) return null

  return (
    <Button
      id="btn-clear-filter-test-plan"
      icon={<ResetIcon width={16} height={16} />}
      onClick={onClear}
      ghost
      className={styles.clearFilter}
      style={{ gap: 4, width: "fit-content" }}
    >
      {t("Clear")}
    </Button>
  )
}
