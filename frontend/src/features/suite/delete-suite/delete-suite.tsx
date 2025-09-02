import { DeleteOutlined } from "@ant-design/icons"
import { Button } from "antd"
import { ReactNode, memo, useState } from "react"
import { useTranslation } from "react-i18next"

import { DeleteTestSuiteModal } from "./delete-test-suite-modal"

interface Props {
  as?: ReactNode
  suite: Suite
  onSubmit?: (suite: Suite) => void
}

export const DeleteSuite = memo(({ as, suite, onSubmit }: Props) => {
  const { t } = useTranslation()
  const [isShowTestSuiteDeleteModal, setIsShowTestSuiteDeleteModal] = useState(false)

  const handleShow = () => {
    setIsShowTestSuiteDeleteModal(true)
  }

  return (
    <>
      {as ? (
        <div id="delete-test-suite" onClick={handleShow}>
          {as}
        </div>
      ) : (
        <Button id="delete-test-suite" icon={<DeleteOutlined />} onClick={handleShow}>
          {t("Delete")}
        </Button>
      )}
      <DeleteTestSuiteModal
        testSuite={suite}
        isShow={isShowTestSuiteDeleteModal}
        setIsShow={setIsShowTestSuiteDeleteModal}
        onSubmit={onSubmit}
      />
    </>
  )
})

DeleteSuite.displayName = "DeleteSuite"
