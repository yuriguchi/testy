import { CopyOutlined } from "@ant-design/icons"
import { Button, Tooltip } from "antd"
import { useState } from "react"
import { useTranslation } from "react-i18next"

import { TestResultEditCloneModal } from "./test-result-edit-clone-modal"

interface Props {
  testCase: TestCase
  testResult: Result
  isDisabled: boolean
  isClone: boolean
  onSubmit?: (newResult: Result, oldResult: Result) => void
}

export const EditCloneResult = ({ testCase, testResult, isDisabled, isClone, onSubmit }: Props) => {
  const { t } = useTranslation()
  const [isShow, setIsShow] = useState(false)

  return (
    <>
      <Button
        id={`edit${isClone ? "-clone" : ""}-result`}
        onClick={() => setIsShow(true)}
        type="link"
        style={{
          border: "none",
          padding: 0,
          height: "auto",
          lineHeight: 1,
        }}
        disabled={isDisabled}
      >
        <span style={{ textDecoration: "underline" }}>
          {!isClone ? (
            t("Edit")
          ) : (
            <Tooltip placement="topRight" title={t("Clone test result")}>
              <CopyOutlined />
            </Tooltip>
          )}
        </span>
      </Button>
      <TestResultEditCloneModal
        isShow={isShow}
        setIsShow={setIsShow}
        testResult={testResult}
        testCase={testCase}
        isClone={isClone}
        onSubmit={onSubmit}
      />
    </>
  )
}
