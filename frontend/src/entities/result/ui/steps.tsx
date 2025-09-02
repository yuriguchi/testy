import { Divider } from "antd"
import { useTranslation } from "react-i18next"

import { Steps } from "shared/ui"

interface TestResultStepsProps {
  stepsResult: StepResult[]
}

export const TestResultSteps = ({ stepsResult }: TestResultStepsProps) => {
  const { t } = useTranslation()

  return (
    <>
      <Divider orientation="left" style={{ margin: 0, fontSize: 14 }}>
        {t("Steps")}
      </Divider>
      <Steps.Result stepsResult={stepsResult} />
    </>
  )
}
