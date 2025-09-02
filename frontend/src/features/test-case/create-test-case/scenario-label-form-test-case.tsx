import { Flex } from "antd"
import { Control, Controller } from "react-hook-form"
import { useTranslation } from "react-i18next"

import { Toggle } from "shared/ui"

export const ScenarioLabelFormTestCase = ({
  control,
}: {
  control: Control<TestCaseFormData, unknown>
}) => {
  const { t } = useTranslation()
  return (
    <Flex style={{ width: "100%" }} align="center" justify="space-between">
      <span>{t("Scenario")}</span>
      <Controller
        name="is_steps"
        control={control}
        render={({ field }) => (
          <Toggle
            id="edit-steps-toggle"
            label={t("Steps")}
            checked={field.value}
            onChange={field.onChange}
            size="sm"
          />
        )}
      />
    </Flex>
  )
}
