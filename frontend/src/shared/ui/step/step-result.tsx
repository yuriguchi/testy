import { Status } from "shared/ui"

import styles from "./styles.module.css"

interface StepResultProps {
  stepsResult: StepResult[]
}

export const StepResult = ({ stepsResult }: StepResultProps) => {
  return (
    <ul className={styles.fieldUl}>
      {[...stepsResult]
        .sort((a, b) => a.sort_order - b.sort_order)
        .map((stepResult) => (
          <li
            id={`step-item-${stepResult.name}`}
            className={styles.resultFieldItem}
            key={stepResult.id}
          >
            <div className={styles.resultFieldIcon}>{stepResult.sort_order}</div>
            <div className={styles.resultFieldWrapper}>
              <span>{stepResult.name}</span>
            </div>
            <div className={styles.resultStatus}>
              <Status
                name={stepResult.status_text}
                id={stepResult.status}
                color={stepResult.status_color}
              />
            </div>
          </li>
        ))}
    </ul>
  )
}
