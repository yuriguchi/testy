import { Checkbox } from "antd"
import { useTranslation } from "react-i18next"

import styles from "./styles.module.css"

interface Props {
  value: CustomAttributeAppliedToUpdate
  onChange: (value: CustomAttributeAppliedToUpdate) => void
}

export const TestSuiteTypeForm = ({ value, onChange }: Props) => {
  const { t } = useTranslation()

  const handleRequiredChange = () => {
    onChange({
      ...value,
      testsuite: { ...value.testsuite, is_required: !value.testsuite.is_required },
    })
  }

  return (
    <div className={styles.wrapper}>
      <Checkbox
        data-testid="checkbox-is-required"
        className="checkbox-md"
        checked={value.testsuite.is_required}
        onChange={handleRequiredChange}
      >
        {t("Required")}
      </Checkbox>
    </div>
  )
}
