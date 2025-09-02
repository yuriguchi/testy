import { useEffect, useMemo, useState } from "react"
import { UseFormSetValue } from "react-hook-form"
import { useParams } from "react-router-dom"

import { useGetLabelsQuery } from "../api"

export interface UseFormLabelsProps {
  labels: LabelInForm[]
  searchValue: string
  setLabels: React.Dispatch<React.SetStateAction<LabelInForm[]>>
  setSearchValue: React.Dispatch<React.SetStateAction<string>>
  isShowPopup: boolean
  setIsShowPopup: React.Dispatch<React.SetStateAction<boolean>>
  searchingLabels: Label[]
  handleAddLabel: (label: string) => void
  handleDeleteLabel: (label: string) => void
  handleSubmitInput: (e: React.KeyboardEvent<HTMLInputElement>, label: string) => void
}

interface UseTestCaseFormLabelsParams {
  setValue: UseFormSetValue<TestCaseFormData>
  testCase: TestCase | null
  isShow: boolean
  isEditMode: boolean
  defaultLabels?: number[]
}

export const useTestCaseFormLabels = ({
  setValue,
  testCase,
  isShow,
  isEditMode,
  defaultLabels = [],
}: UseTestCaseFormLabelsParams): UseFormLabelsProps => {
  const { projectId } = useParams<ParamProjectId>()
  const [labels, setLabels] = useState<LabelInForm[]>([])
  const [searchValue, setSearchValue] = useState("")
  const [isShowPopup, setIsShowPopup] = useState(false)
  const { data: labelsData } = useGetLabelsQuery(
    { project: projectId ?? "" },
    { skip: !projectId || !isShow }
  )
  const handleAddLabel = (label: string) => {
    const filtered = labels.filter((item) => item.name.toLowerCase() !== label.toLowerCase())
    const labelData = labelsData?.find((item) => item.name.toLowerCase() === label.toLowerCase())

    const newLabels = [...filtered, { name: label, id: labelData?.id }]
    setLabels(newLabels)
    setSearchValue("")
    setIsShowPopup(false)
    setValue("labels", newLabels, { shouldDirty: true })
  }

  const handleDeleteLabel = (label: string) => {
    const filtered = labels.filter((item) => item.name !== label)
    setLabels(filtered)
    setValue("labels", filtered, { shouldDirty: true })
  }

  const handleSubmitInput = (e: React.KeyboardEvent<HTMLInputElement>, label: string) => {
    if (e.key !== "Enter") return
    handleAddLabel(label)
  }

  useEffect(() => {
    setIsShowPopup(!!searchValue.length)
  }, [searchValue])

  useEffect(() => {
    if (!testCase || !isEditMode) return
    setLabels(testCase.labels)
    setValue("labels", testCase.labels)
  }, [testCase, isShow, isEditMode])

  const withoutDublicateLabels = useMemo(() => {
    if (!labelsData) return []
    if (!labels.length) return labelsData

    return labelsData.filter(
      ({ name: name1 }) => !labels.some(({ name: name2 }) => name1 === name2)
    )
  }, [labels, labelsData])

  useEffect(() => {
    if (!labelsData) return

    setLabels(
      labelsData.filter(
        (label) =>
          label.id &&
          defaultLabels.includes(typeof label.id === "number" ? label.id : parseInt(label.id))
      )
    )
  }, [labelsData])

  const searchingLabels = useMemo(() => {
    return withoutDublicateLabels.filter((label) =>
      label.name.toLowerCase().includes(searchValue.toLowerCase())
    )
  }, [searchValue, withoutDublicateLabels])

  return {
    labels,
    searchingLabels,
    searchValue,
    isShowPopup,
    setLabels,
    setSearchValue,
    setIsShowPopup,
    handleAddLabel,
    handleDeleteLabel,
    handleSubmitInput,
  }
}
