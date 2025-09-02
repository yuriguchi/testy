import { DeleteOutlined } from "@ant-design/icons"
import { Button } from "antd"
import { useState } from "react"
import { useTranslation } from "react-i18next"

import { DeleteTestCaseModal } from "./delete-test-case-modal"

interface Props {
  testCase: TestCase
  onSubmit?: (testCase: TestCase) => void
}

export const DeleteTestCase = ({ testCase, onSubmit }: Props) => {
  const { t } = useTranslation()
  const [isShowTestCaseDeleteModal, setIsShowTestCaseDeleteModal] = useState(false)

  const handleDelete = () => {
    setIsShowTestCaseDeleteModal(true)
  }

  return (
    <>
      <Button id="delete-test-case-detail" onClick={handleDelete} icon={<DeleteOutlined />} danger>
        {t("Delete")}
      </Button>
      <DeleteTestCaseModal
        isShow={isShowTestCaseDeleteModal}
        setIsShow={setIsShowTestCaseDeleteModal}
        testCase={testCase}
        onSubmit={onSubmit}
      />
    </>
  )
}
