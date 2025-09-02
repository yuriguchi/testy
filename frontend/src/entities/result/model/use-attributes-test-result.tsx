import { useGetCustomAttributesQuery } from "entities/custom-attribute/api"
import { convertAttribute } from "entities/custom-attribute/lib"
import { useAttributes } from "entities/custom-attribute/model"
import { useStatuses } from "entities/status/model/use-statuses"
import { useContext, useMemo } from "react"
import { UseFormSetValue } from "react-hook-form"

import { useAppSelector } from "app/hooks"

import { selectDrawerTest } from "entities/test/model"

import { ProjectContext } from "pages/project"

interface UseAttributesProps {
  mode: "create" | "edit"
  setValue: UseFormSetValue<ResultFormData>
}

export const useAttributesTestResult = ({ mode, setValue }: UseAttributesProps) => {
  const { project } = useContext(ProjectContext)!
  const { allStatusesId } = useStatuses({ project: project.id })

  const selectedDrawerTest = useAppSelector(selectDrawerTest)

  const { data, isLoading } = useGetCustomAttributesQuery(
    { project: String(project.id), test: selectedDrawerTest?.id },
    { skip: !selectedDrawerTest }
  )

  const initAttributes = useMemo(() => {
    if (!data) return []

    return data
      .filter((i) => i.applied_to.testresult)
      .filter((attribute) =>
        !!attribute.applied_to.testresult.suite_ids.length && selectedDrawerTest?.suite
          ? attribute.applied_to.testresult.suite_ids.includes(selectedDrawerTest?.suite)
          : true
      )
      .map((i) => convertAttribute({ attribute: i, model: "testresult" }))
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
      status_specific: allStatusesId,
    },
    getJsonAdditionalParams: {
      required: false,
      status_specific: allStatusesId,
    },
  })

  return {
    attributes,
    isLoading,
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
