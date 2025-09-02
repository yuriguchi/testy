import { EditOutlined, PlusOutlined } from "@ant-design/icons"
import { Button } from "antd"
import { BaseButtonProps } from "antd/es/button/button"
import { ReactNode, memo } from "react"
import { useTranslation } from "react-i18next"
import { useNavigate, useParams } from "react-router-dom"

interface Props {
  type: "create" | "edit"
  as?: ReactNode
  suite?: Suite
  size?: "small" | "default"
  colorType?: BaseButtonProps["type"]
}

export const ChangeTestSuite = memo(
  ({ type, as, suite, size = "default", colorType = "default" }: Props) => {
    const { t } = useTranslation()
    const { projectId, testSuiteId } = useParams<ParamProjectId | ParamTestSuiteId>()

    const navigate = useNavigate()

    const handleClick = () => {
      const url = new URL(
        `${window.location.origin}/projects/${projectId}/suites/${type === "create" ? "new" : `${suite?.id}/edit`}-test-suite`
      )
      const currentSearchParams = new URLSearchParams(window.location.search)

      const parentTestSuite =
        (type === "create" ? suite?.id.toString() : suite?.parent?.id.toString()) ?? testSuiteId
      if (parentTestSuite) {
        url.searchParams.append("parentTestSuite", parentTestSuite)
      }

      url.searchParams.append(
        "prevUrl",
        !currentSearchParams.get("prevUrl")
          ? `${window.location.pathname}${window.location.search}`
          : (currentSearchParams.get("prevUrl") ?? "")
      )

      navigate(`${url.pathname}${url.search}`, { state: { suite } })
    }

    const getButtonTitle = () => {
      if (size === "small") {
        return ""
      }

      if (type === "create") {
        return !suite ? t("Create") : t("Create Child Test Suite")
      } else {
        return t("Edit")
      }
    }

    const getButtonId = () => {
      if (type === "create") {
        return !suite ? "create-test-suite" : "create-child-test-suite"
      } else {
        return "edit-test-suite"
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
        shape={size === "default" ? "default" : "circle"}
      >
        {getButtonTitle()}
      </Button>
    )
  }
)

ChangeTestSuite.displayName = "ChangeTestSuite"
