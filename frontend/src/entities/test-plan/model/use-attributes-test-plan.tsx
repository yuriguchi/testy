import { useGetCustomAttributesQuery } from "entities/custom-attribute/api"
import { convertAttribute } from "entities/custom-attribute/lib"
import { useAttributes } from "entities/custom-attribute/model"
import { useContext, useMemo } from "react"
import { UseFormSetValue } from "react-hook-form"

import { ChangeTestPlanForm } from "features/test-plan/change-test-plan/use-change-test-plan"

import { ProjectContext } from "pages/project"

interface UseAttributesProps {
  mode: "create" | "edit"
  setValue: UseFormSetValue<ChangeTestPlanForm>
}

export const useAttributesTestPlan = ({ mode, setValue }: UseAttributesProps) => {
  const { project } = useContext(ProjectContext)!

  const { data, isLoading } = useGetCustomAttributesQuery({ project: String(project.id) })

  const initAttributes = useMemo(() => {
    if (!data) return []

    return data
      .filter((i) => i.applied_to.testplan)
      .map((i) => convertAttribute({ attribute: i, model: "testplan" }))
  }, [data])

  const handleSetValue = (attributes: Attribute[]) => {
    setValue("attributes", attributes, { shouldDirty: true })
  }

  const {
    attributes,
    addAttribute,
    getAttributeJson,
    onAttributeChangeName,
    onAttributeChangeType,
    onAttributeChangeValue,
    onAttributeRemove,
    resetAttributes,
    setAttributes,
  } = useAttributes({
    mode,
    initAttributes,
    setValue: handleSetValue,
    addAttributeAdditionalParams: {
      required: false,
    },
    getJsonAdditionalParams: {
      required: false,
    },
  })

  return {
    attributes,
    isLoading,
    initAttributes,
    setAttributes,
    resetAttributes,
    addAttribute,
    onAttributeChangeType,
    onAttributeChangeValue,
    onAttributeChangeName,
    onAttributeRemove,
    getAttributeJson,
  }
}
