import { Select } from "antd"
import { useStatuses } from "entities/status/model/use-statuses"
import { useTranslation } from "react-i18next"

import { Status } from "../status"
import styles from "./styles.module.css"

interface StepResultProps {
  testCase: TestCase
  steps: Record<string, number>
  setSteps: React.Dispatch<React.SetStateAction<Record<string, number>>>
}

export const StepResultInCreateModal = ({ testCase, steps, setSteps }: StepResultProps) => {
  const { t } = useTranslation()
  const { statusesOptions, getStatusById } = useStatuses({ project: testCase.project })

  if (!testCase.steps) return <></>

  const handleChange = (stepId: string, statusIdStr: string) => {
    const statusId = parseInt(statusIdStr)
    const status = getStatusById(statusId)
    if (!status) return

    setSteps((prevState) => ({ ...prevState, [stepId]: status.id }))
  }

  return (
    <ul style={{ paddingLeft: 0 }} className={styles.fieldUl}>
      {testCase.steps.map((item) => {
        return (
          <li id={`step-item-${item.name}`} className={styles.resultFieldItem} key={item.id}>
            <div className={styles.resultFieldIcon}>{item.sort_order}</div>
            <div className={styles.resultModalFieldWrapper}>
              <div className={styles.resultModalFieldContent}>
                <div>{item.name}</div>
              </div>
            </div>
            <div className={styles.resultSelect}>
              <Select
                value={steps[item.id]}
                placeholder={t("Please select")}
                style={{ width: "100%" }}
                onSelect={(statusIdStr) => handleChange(item.id, statusIdStr.toString())}
                id={`create-result-step-${item.name}`}
              >
                {statusesOptions.map((status) => (
                  <Select.Option key={status.id} value={status.id}>
                    <Status
                      id={status.id}
                      name={status.label}
                      color={status.color}
                      extraId={`create-result-step-${item.name}`}
                    />
                  </Select.Option>
                ))}
              </Select>
            </div>
          </li>
        )
      })}
    </ul>
  )
}
