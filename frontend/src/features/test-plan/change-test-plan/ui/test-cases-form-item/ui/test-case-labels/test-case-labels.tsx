import { Tooltip, Typography } from "antd"
import { useTranslation } from "react-i18next"

import { Label } from "entities/label/ui"

import styles from "./styles.module.css"

interface LabelProps {
  labels: string[]
}

const MAX_SHOW_LABELS = 3

export const TestCaseLabels = ({ labels }: LabelProps) => {
  const { t } = useTranslation()
  const shownLabels = labels.slice(0, MAX_SHOW_LABELS)

  return (
    <div className={styles.labels} data-testid="test-case-labels">
      {shownLabels.map((label) => (
        <Label key={label} content={label} data-testid={`test-case-label-${label}`} />
      ))}
      {labels.length > MAX_SHOW_LABELS && (
        <Tooltip title={`${t("Labels")}: ${labels.join(", ")}`}>
          <Typography.Text className={styles.extra}>
            {/* {`+ ${labels.length - MAX_SHOW_LABELS}`} */}
            ...
          </Typography.Text>
        </Tooltip>
      )}
    </div>
  )
}
