import { Select } from "antd"
import { useStatuses } from "entities/status/model/use-statuses"
import { useTranslation } from "react-i18next"
import { useParams } from "react-router-dom"

import { Status } from "../status"
import styles from "./styles.module.css"

interface StepResultProps {
  stepResultsData: StepResult[]
  stepResults: Record<string, number>
  setStepsResult: (steps: Record<string, number>) => void
  id: string
}

export const StepResultInEditModal = ({
  stepResultsData,
  stepResults,
  setStepsResult,
  id,
}: StepResultProps) => {
  const { t } = useTranslation()
  const { projectId } = useParams<ParamProjectId>()
  const { statusesOptions } = useStatuses({ project: projectId })
  const handleStepChange = (stepId: string, value: number) => {
    setStepsResult({ ...stepResults, [stepId]: value })
  }

  if (!stepResultsData.length) return <></>

  return (
    <ul style={{ paddingLeft: 0 }} className={styles.fieldUl}>
      {[...stepResultsData]
        .sort((a, b) => a.sort_order - b.sort_order)
        .map((item) => (
          <li id={`step-item-${item.name}`} className={styles.resultFieldItem} key={item.id}>
            <div className={styles.resultFieldIcon}>{item.sort_order}</div>
            <div className={styles.resultModalFieldWrapper}>
              <div className={styles.resultModalFieldContent}>
                <div>{item.name}</div>
              </div>
            </div>
            <div className={styles.resultSelect}>
              <Select
                value={stepResults[item.id] ?? null}
                placeholder={t("Please select")}
                style={{ width: "100%" }}
                onSelect={(value) => handleStepChange(String(item.id), value)}
                id={`${id}-result-step-${item.name}`}
              >
                {statusesOptions.map((status) => (
                  <Select.Option key={status.id} value={Number(status.id)}>
                    <Status
                      name={status.label}
                      color={status.color}
                      id={status.id}
                      extraId={`${id}-result-step-${item.name}`}
                    />
                  </Select.Option>
                ))}
              </Select>
            </div>
          </li>
        ))}
    </ul>
  )
}
