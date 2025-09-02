import { Divider } from "antd"
import { useTranslation } from "react-i18next"

import { StepFieldItem } from "./step-field-item"

interface StepFieldProps {
  steps: Step[]
}

export const StepField = ({ steps }: StepFieldProps) => {
  const { t } = useTranslation()

  return (
    <>
      <Divider orientation="left" style={{ margin: 0 }} orientationMargin={0}>
        {t("Steps")}
      </Divider>
      <ul style={{ paddingLeft: 0, marginTop: 8 }}>
        {steps.map((step) => (
          <StepFieldItem key={step.id} step={step} />
        ))}
      </ul>
    </>
  )
}
