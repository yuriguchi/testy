import { Button } from "antd"
import { useTranslation } from "react-i18next"

interface Props {
  steps: (Step | StepResult)[]
  status: number | null
  onApply: (stepsData: Record<string, number>) => void
}

export const ApplyToStepsButton = ({ steps, status, onApply }: Props) => {
  const { t } = useTranslation()

  const handleApply = () => {
    if (status) {
      const updatedSteps: Record<string, number> = {}
      steps.forEach((step) => {
        if (step.id !== undefined && step.id !== null) {
          updatedSteps[step.id.toString()] = status
        }
      })
      onApply(updatedSteps)
    }
  }

  if (steps.length === 0) {
    return null
  }

  return (
    <Button disabled={!status} onClick={handleApply}>
      {t("Apply to steps")}
    </Button>
  )
}
