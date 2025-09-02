import { PlusOutlined } from "@ant-design/icons"
import { Button } from "antd"
import { useState } from "react"
import { useTranslation } from "react-i18next"

import { CreateResultModal } from "./create-result-modal"

interface Props {
  isDisabled: boolean
  testCase: TestCase
  onSubmit?: (result: Result) => void
}

export const AddResult = ({ isDisabled, testCase, onSubmit }: Props) => {
  const { t } = useTranslation()
  const [isShow, setIsShow] = useState(false)

  return (
    <>
      <Button
        id="add-result-btn"
        type="primary"
        onClick={() => setIsShow(true)}
        icon={<PlusOutlined />}
        disabled={isDisabled}
      >
        {t("Add Result")}
      </Button>
      <CreateResultModal
        isShow={isShow}
        setIsShow={setIsShow}
        testCase={testCase}
        onSubmit={onSubmit}
      />
    </>
  )
}
