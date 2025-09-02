import { EditOutlined } from "@ant-design/icons"
import { Button } from "antd"
import { ReactNode, memo, useState } from "react"
import { useTranslation } from "react-i18next"

import { EditTestPlanModal } from "./edit-test-plan-modal"

interface Props {
  as?: ReactNode
  testPlan: TestPlan
  onSubmit?: (updatedPlan: TestPlan, oldPlan: TestPlan) => void
}

export const EditTestPlan = memo(({ as, testPlan, onSubmit }: Props) => {
  const { t } = useTranslation()
  const [isShow, setIsShow] = useState(false)

  const handleShow = () => {
    setIsShow(true)
  }

  return (
    <>
      {as ? (
        <div id="edit-test-plan" onClick={handleShow}>
          {as}
        </div>
      ) : (
        <Button
          id="edit-test-plan"
          disabled={testPlan.is_archive}
          onClick={handleShow}
          icon={<EditOutlined />}
        >
          {t("Edit")}
        </Button>
      )}

      <EditTestPlanModal
        isShow={isShow}
        setIsShow={setIsShow}
        testPlan={testPlan}
        onSubmit={onSubmit}
      />
    </>
  )
})

EditTestPlan.displayName = "EditTestPlan"
