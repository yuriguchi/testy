import { PlusOutlined } from "@ant-design/icons"
import { Button } from "antd"
import { BaseButtonProps } from "antd/es/button/button"
import { ReactNode, memo, useState } from "react"
import { useTranslation } from "react-i18next"

import { CreateTestPlanModal } from "./create-test-plan-modal"

interface Props {
  as?: ReactNode
  testPlan?: TestPlan
  size?: "small" | "default"
  onSubmit?: (plan: TestPlan) => void
  colorType?: BaseButtonProps["type"]
}

export const CreateTestPlan = memo(
  ({ as, testPlan, onSubmit, size = "default", colorType = "default" }: Props) => {
    const { t } = useTranslation()
    const [isShow, setIsShow] = useState(false)

    const handleShow = () => {
      setIsShow(true)
    }

    const BUTTON_TITLE =
      size === "default" ? (!testPlan ? t("Create") : t("Create Child Test Plan")) : ""

    return (
      <>
        {as ? (
          <div id={!testPlan ? "create-test-plan" : "create-child-test-plan"} onClick={handleShow}>
            {as}
          </div>
        ) : (
          <Button
            id={!testPlan ? "create-test-plan" : "create-child-test-plan"}
            icon={<PlusOutlined />}
            onClick={handleShow}
            type={colorType}
            disabled={testPlan?.is_archive}
            shape={size === "default" ? "default" : "circle"}
          >
            {BUTTON_TITLE}
          </Button>
        )}
        <CreateTestPlanModal
          isShow={isShow}
          setIsShow={setIsShow}
          testPlan={testPlan}
          onSubmit={onSubmit}
        />
      </>
    )
  }
)

CreateTestPlan.displayName = "CreateTestPlan"
