import { Button, Flex } from "antd"
import classNames from "classnames"
import { useTranslation } from "react-i18next"

import styles from "./styles.module.css"

interface Props {
  value: LabelCondition
  onChange: (value: LabelCondition) => void
  disabled?: boolean
}

export const LabelFilterCondition = ({ value, onChange, disabled = false }: Props) => {
  const { t } = useTranslation()

  return (
    <Flex>
      <Button
        htmlType="button"
        className={classNames(styles.btn, {
          [styles.btnInActive]: value !== "and",
        })}
        onClick={() => onChange("and")}
        disabled={disabled}
        data-testid="label-filter-condition-and"
      >
        {t("and").toUpperCase()}
      </Button>
      <Button
        htmlType="button"
        className={classNames(styles.btn, {
          [styles.btnInActive]: value !== "or",
        })}
        onClick={() => onChange("or")}
        disabled={disabled}
        data-testid="label-filter-condition-or"
      >
        {t("or").toUpperCase()}
      </Button>
    </Flex>
  )
}
