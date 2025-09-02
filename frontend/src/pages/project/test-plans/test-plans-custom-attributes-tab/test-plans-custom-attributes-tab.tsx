import { Flex } from "antd"
import { CustomAttributeInTab } from "entities/custom-attribute/ui"
import { useTranslation } from "react-i18next"

import { useTestPlanContext } from "../test-plan-layout/test-plan-layout"

export const TestPlansCustomAttributesTab = () => {
  const { t } = useTranslation()
  const { testPlan } = useTestPlanContext()

  if (!testPlan || !Object.keys(testPlan.attributes).length) {
    return <p>{t("No custom attributes")}</p>
  }

  return (
    <Flex vertical>
      {Object.entries(testPlan.attributes).map(([title, value], index) => (
        <CustomAttributeInTab key={index} title={title} value={value} isRequired={false} />
      ))}
    </Flex>
  )
}
