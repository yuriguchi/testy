import { EditOutlined, PlusOutlined } from "@ant-design/icons"
import { Button } from "antd"
import { BaseButtonProps } from "antd/es/button/button"
import { ReactNode, memo } from "react"
import { useTranslation } from "react-i18next"
import { useNavigate, useParams } from "react-router-dom"

interface Props {
  type: "create" | "edit"
  as?: ReactNode
  testPlan?: TestPlan
  size?: "small" | "default"
  colorType?: BaseButtonProps["type"]
}

export const ChangeTestPlan = memo(
  ({ type, as, testPlan, size = "default", colorType = "default" }: Props) => {
    const { t } = useTranslation()
    const { projectId, testPlanId } = useParams<ParamProjectId | ParamTestPlanId>()

    const navigate = useNavigate()

    const handleClick = () => {
      const url = new URL(
        `${window.location.origin}/projects/${projectId}/plans/${type === "create" ? "new" : `${testPlan?.id}/edit`}-test-plan`
      )
      const currentSearchParams = new URLSearchParams(window.location.search)

      const parentTestPlan =
        (type === "create" ? testPlan?.id.toString() : testPlan?.parent?.id.toString()) ??
        testPlanId
      if (parentTestPlan) {
        url.searchParams.append("parentTestPlan", parentTestPlan)
      }

      url.searchParams.append(
        "prevUrl",
        !currentSearchParams.get("prevUrl")
          ? `${window.location.pathname}${window.location.search}`
          : (currentSearchParams.get("prevUrl") ?? "")
      )

      navigate(`${url.pathname}${url.search}`, { state: { testPlan } })
    }

    const getButtonTitle = () => {
      if (size === "small") {
        return ""
      }

      if (type === "create") {
        return !testPlan ? t("Create") : t("Create Child Test Plan")
      } else {
        return t("Edit")
      }
    }

    const getButtonId = () => {
      if (type === "create") {
        return !testPlan ? "create-test-plan" : "create-child-test-plan"
      } else {
        return "edit-test-plan"
      }
    }

    if (as) {
      return (
        <div id={getButtonId()} onClick={handleClick}>
          {as}
        </div>
      )
    }

    return (
      <Button
        id={getButtonId()}
        icon={type === "create" ? <PlusOutlined /> : <EditOutlined />}
        onClick={handleClick}
        type={colorType}
        disabled={testPlan?.is_archive}
        shape={size === "default" ? "default" : "circle"}
      >
        {getButtonTitle()}
      </Button>
    )
  }
)

ChangeTestPlan.displayName = "ChangeTestPlan"
