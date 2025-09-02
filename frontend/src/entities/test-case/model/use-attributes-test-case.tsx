import { useGetCustomAttributesQuery } from "entities/custom-attribute/api"
import { convertAttribute } from "entities/custom-attribute/lib"
import { useAttributes } from "entities/custom-attribute/model"
import { useMemo } from "react"
import { UseFormSetValue } from "react-hook-form"
import { useParams } from "react-router-dom"

interface UseAttributesProps {
  mode: "create" | "edit"
  setValue: UseFormSetValue<TestCaseFormData>
}

export const useAttributesTestCase = ({ mode, setValue }: UseAttributesProps) => {
  const { projectId, testSuiteId } = useParams<ParamProjectId & ParamTestSuiteId>()

  const { data, isLoading: isLoadingCustomAttributes } = useGetCustomAttributesQuery(
    { project: projectId ?? "" },
    { skip: !projectId }
  )

  const initAttributes = useMemo(() => {
    if (!data) return []

    return data
      .filter((i) => i.applied_to.testcase)
      .filter((attribute) =>
        !!attribute.applied_to.testcase.suite_ids.length && testSuiteId
          ? attribute.applied_to.testcase.suite_ids.includes(Number(testSuiteId))
          : true
      )
      .map((i) => convertAttribute({ attribute: i, model: "testcase" }))
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
    getJsonAdditionalParams: {
      required: false,
    },
  })

  return {
    attributes,
    isLoading: isLoadingCustomAttributes,
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
