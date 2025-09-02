import { notification } from "antd"
import dayjs from "dayjs"
import React, { useEffect, useState } from "react"
import { SubmitHandler, useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"
import { useParams } from "react-router-dom"

import { useAttachments } from "entities/attachment/model"

import { useGetParametersQuery } from "entities/parameter/api"

import { useCreateTestPlanMutation, useGetTestPlanQuery } from "entities/test-plan/api"
import { getTestCaseChangeResult } from "entities/test-plan/lib"

import { useShowModalCloseConfirm } from "shared/hooks"
import { makeParametersForTreeView } from "shared/libs"
import { AlertSuccessChange } from "shared/ui"

import { ModalForm, useTestPlanCommonModal } from "./use-test-plan-common-modal"

type IForm = ModalForm<TestPlanCreate>

interface UseTestPlanCreateModalProps {
  isShow: boolean
  setIsShow: React.Dispatch<React.SetStateAction<boolean>>
  testPlan?: TestPlan
  onSubmit?: (plan: TestPlan) => void
}

const defaultValues: { defaultValues: Partial<IForm> } = {
  defaultValues: {
    name: "",
    description: "",
    test_cases: [],
    parameters: [],
    attachments: [],
    parent: null,
    started_at: dayjs(),
    due_date: dayjs().add(1, "day"),
  },
}

export const useTestPlanCreateModal = ({
  isShow,
  setIsShow,
  testPlan: initTestPlan,
  onSubmit: onSubmitCb,
}: UseTestPlanCreateModalProps) => {
  const { t } = useTranslation()
  const { showModal } = useShowModalCloseConfirm()
  const { testPlanId } = useParams<ParamTestPlanId>()

  const {
    handleSubmit,
    reset,
    control,
    setValue,
    formState: { isDirty, errors: formErrors },
    watch,
  } = useForm<IForm>(defaultValues)

  const testCasesWatch = watch("test_cases")

  const [parametersTreeView, setParametersTreeView] = useState<IParameterTreeView[]>([])

  const [createTestPlan, { isLoading: isLoadingCreateTestPlan }] = useCreateTestPlanMutation()

  const {
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
  } = useTestPlanCommonModal({ isShow })

  const { data: testPlanFromParams } = useGetTestPlanQuery(
    { testPlanId: String(testPlanId), project: Number(projectId) },
    { skip: !testPlanId || !isShow }
  )
  const { data: parameters } = useGetParametersQuery(Number(projectId), {
    skip: !projectId || !isShow,
  })

  const testPlan = testPlanId ? (initTestPlan ?? testPlanFromParams) : initTestPlan

  const {
    attachments,
    attachmentsIds,
    isLoading: isLoadingAttachments,
    setAttachments,
    onLoad,
  } = useAttachments<IForm>(control, Number(projectId))

  useEffect(() => {
    if (!isShow || !testPlan) return
    reset({
      ...defaultValues.defaultValues,
      parent: testPlan.id,
    })
    setSelectedParent({ value: testPlan.id, label: testPlan.name })
  }, [testPlan, isShow])

  useEffect(() => {
    if (parameters) {
      setParametersTreeView(makeParametersForTreeView(parameters))
    }
  }, [parameters])

  const onCloseModal = () => {
    setSelectedParent(null)
    setValue("parent", null)
    setIsShow(false)
    setErrors(null)
    reset()
    onClearSearch()
  }

  const handleClose = () => {
    if (isLoadingCreateTestPlan) {
      return
    }

    if (isDirty) {
      showModal(onCloseModal)
      return
    }

    onCloseModal()
  }

  const onSubmit: SubmitHandler<IForm> = async (data) => {
    setErrors(null)
    try {
      const newTestCases = data.test_cases?.filter((item) => !item.startsWith("TS"))
      const newTestPlan = await createTestPlan({
        ...data,
        test_cases: newTestCases,
        project: Number(projectId),
      }).unwrap()
      onCloseModal()
      notification.success({
        message: t("Success"),
        closable: true,
        description: (
          <AlertSuccessChange
            id={String(newTestPlan[0].id)}
            action="created"
            title={t("Test Plan")}
            link={`/projects/${projectId}/plans/${newTestPlan[0].id}`}
          />
        ),
      })
      onSubmitCb?.(newTestPlan[0])
    } catch (err: unknown) {
      onHandleError(err)
    }
  }

  const handleSelectTestPlan = (value: SelectData | null) => {
    setErrors({ parent: "" })
    if (Number(value?.value) === Number(testPlan?.id)) {
      setErrors({ parent: t("Test Plan cannot be its own parent.") })
      return
    }

    setValue("parent", value ? value.value : null, { shouldDirty: true })
    setSelectedParent(value ? { value: value.value, label: value.label?.toString() ?? "" } : null)
  }

  const handleTestCaseChange = (checked: CheckboxChecked, info: TreeCheckboxInfo) => {
    const result = getTestCaseChangeResult(checked, info, testCasesWatch)
    setValue("test_cases", result, { shouldDirty: true })
  }

  return {
    attachments,
    attachmentsIds,
    isLoading: isLoadingAttachments,
    setAttachments,
    onLoad,
    isLoadingCreateTestPlan,
    isDirty,
    errors,
    formErrors,
    control,
    searchText,
    expandedRowKeys,
    treeData,
    parametersTreeView,
    selectedParent,
    isLoadingTreeData,
    handleRowExpand: onRowExpand,
    handleSearch: onSearch,
    handleSubmitForm: handleSubmit(onSubmit),
    handleClose,
    setDateFrom,
    setDateTo,
    disabledDateFrom,
    disabledDateTo,
    setValue,
    handleTestCaseChange,
    handleSelectTestPlan,
    selectedLables,
    labelProps,
    lableCondition,
    handleConditionClick,
    showArchived,
    handleToggleArchived,
  }
}
