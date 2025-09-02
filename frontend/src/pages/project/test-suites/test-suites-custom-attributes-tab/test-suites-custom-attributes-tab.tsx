import { Flex } from "antd"
import { CustomAttributeInTab } from "entities/custom-attribute/ui"
import { useTranslation } from "react-i18next"

import { useTestSuiteContext } from "../test-suite-layout"

export const TestSuitesCustomAttributesTab = () => {
  const { t } = useTranslation()
  const { suite } = useTestSuiteContext()

  if (!suite || !Object.keys(suite.attributes).length) {
    return <p>{t("No custom attributes")}</p>
  }

  return (
    <Flex vertical>
      {Object.entries(suite.attributes).map(([title, value], index) => (
        <CustomAttributeInTab key={index} title={title} value={value} isRequired={false} />
      ))}
    </Flex>
  )
}
