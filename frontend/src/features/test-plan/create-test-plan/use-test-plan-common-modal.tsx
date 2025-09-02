import { Dayjs } from "dayjs"
import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"

import { useTestCaseFormLabels } from "entities/label/model"

import { useTestCasesSearch } from "entities/test-case/model"

import { useDatepicker, useErrors } from "shared/hooks"

interface Params {
  isShow: boolean
}

export interface ErrorData {
  name?: string
  description?: string
  parent?: string
  test_cases?: string
  started_at?: string
  due_date?: string
  parameters?: string
}

export type ModalForm<T> = Modify<
  T,
  {
    test_cases: string[]
    started_at: Dayjs
    due_date: Dayjs
  }
>

export const useTestPlanCommonModal = ({ isShow }: Params) => {
  const { projectId } = useParams<ParamProjectId & ParamTestPlanId>()
  const [errors, setErrors] = useState<ErrorData | null>(null)

  const {
    searchText,
    treeData,
    expandedRowKeys,
    isLoading: isLoadingTreeData,
    onSearch,
    onRowExpand,
    onClearSearch,
  } = useTestCasesSearch({ isShow })

  const [selectedLables, setSelectedLabels] = useState<number[]>([])
  // eslint-disable-next-line @typescript-eslint/no-unused-vars, @typescript-eslint/no-explicit-any
  const setLables = (_: string, values: any, data: any) => {
    const v = values as { name: string; id?: number }[]
    setSelectedLabels(v.map((i) => i.id).filter((i) => i !== undefined))
  }

  const labelProps = useTestCaseFormLabels({
    setValue: setLables,
    testCase: null,
    isShow,
    isEditMode: false,
    defaultLabels: selectedLables,
  })

  const [lableCondition, setLableCondition] = useState<LabelCondition>("and")
  const [showArchived, setShowArchived] = useState(false)

  const handleToggleArchived = () => {
    setShowArchived(!showArchived)
  }

  const handleConditionClick = () => {
    setLableCondition(lableCondition === "and" ? "or" : "and")
  }

  useEffect(() => {
    onSearch(searchText, selectedLables, lableCondition, showArchived)
  }, [selectedLables, lableCondition, showArchived])

  const { onHandleError } = useErrors<ErrorData>(setErrors)

  const [selectedParent, setSelectedParent] = useState<{ label: string; value: number } | null>(
    null
  )
  const { setDateFrom, setDateTo, disabledDateFrom, disabledDateTo } = useDatepicker()

  return {
    selectedLables,
    labelProps,
    lableCondition,
    handleConditionClick,
    showArchived,
    handleToggleArchived,
    projectId,
    errors,
    setErrors,
    onHandleError,
    selectedParent,
    setSelectedParent,
    setDateFrom,
    setDateTo,
    disabledDateFrom,
    disabledDateTo,
    searchText,
    treeData,
    expandedRowKeys,
    isLoading: isLoadingTreeData,
    onSearch,
    onRowExpand,
    onClearSearch,
  }
}
