import classNames from "classnames"

import { Toggle } from "shared/ui"

import { TestCaseTypeForm } from "../applied-types/testcase-type-form/testcase-type-form"
import { TestPlanTypeForm } from "../applied-types/testplan-type-form/testplan-type-form"
import { TestResultTypeForm } from "../applied-types/testresult-type-form/testresult-type-form"
import { TestSuiteTypeForm } from "../applied-types/testsuite-type-form/testsuite-type-form"
import TestCaseIcon from "./icons/test-case.svg?react"
import TestPlansIcon from "./icons/test-plans.svg?react"
import TestResultIcon from "./icons/test-result.svg?react"
import TestSuitesIcon from "./icons/test-suites.svg?react"
import styles from "./styles.module.css"

const iconsByModelName = {
  testcase: <TestCaseIcon width={32} height={32} />,
  testresult: <TestResultIcon width={32} height={32} />,
  testplan: <TestPlansIcon width={32} height={32} />,
  testsuite: <TestSuitesIcon width={32} height={32} />,
}

interface Props {
  contentTypes: CustomAttributeContentType[]
  value: CustomAttributeAppliedToUpdate
  onChange: (value: CustomAttributeAppliedToUpdate) => void
}

export const SelectContentTypes = ({ contentTypes, value, onChange }: Props) => {
  const handleItemClick = (type: CustomAttributeContentType) => {
    const typeValue = value[type.model]
    onChange({
      ...value,
      [type.model]: {
        ...typeValue,
        is_active: !typeValue.is_active,
      },
    })
  }

  const formByType = {
    testcase: <TestCaseTypeForm value={value} onChange={onChange} />,
    testresult: <TestResultTypeForm value={value} onChange={onChange} />,
    testplan: <TestPlanTypeForm value={value} onChange={onChange} />,
    testsuite: <TestSuiteTypeForm value={value} onChange={onChange} />,
  }

  return (
    <ul className={styles.list}>
      {contentTypes.map((type) => {
        const isActive = value[type.model].is_active

        return (
          <li
            data-testid={`applied-to-${type.model}`}
            key={type.id}
            className={classNames(styles.item, {
              [styles.active]: isActive,
            })}
          >
            <div className={styles.itemHeader}>
              <Toggle
                id={type.model}
                label={<span className={styles.name}>{type.name}</span>}
                checked={isActive}
                size="lg"
                onChange={() => handleItemClick(type)}
              />
              {iconsByModelName[type.model]}
            </div>
            {isActive && formByType[type.model]}
          </li>
        )
      })}
    </ul>
  )
}
