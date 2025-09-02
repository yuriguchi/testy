import { notification } from "antd"
import dayjs from "dayjs"
import { useEffect } from "react"
import { SubmitHandler, useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"

import { useAttachments } from "entities/attachment/model"

import { useGetTestPlanCasesQuery, useUpdateTestPlanMutation } from "entities/test-plan/api"
import { getTestCaseChangeResult } from "entities/test-plan/lib"

import { useShowModalCloseConfirm } from "shared/hooks"
import { AlertSuccessChange } from "shared/ui"

import { ModalForm, useTestPlanCommonModal } from "../create-test-plan/use-test-plan-common-modal"

type IForm = ModalForm<TestPlanUpdate>

export interface UseTestPlanEditModalProps {
  testPlan: TestPlan
  isShow: boolean
  setIsShow: (isShow: boolean) => void
  onSubmit?: (updatedPlan: TestPlan, oldPlan: TestPlan) => void
}

export const useTestPlanEditModal = ({
  testPlan,
  isShow,
  setIsShow,
  onSubmit: onSubmitCb,
}: UseTestPlanEditModalProps) => {
  const { t } = useTranslation()
  const { showModal } = useShowModalCloseConfirm()
  const {
    handleSubmit,
    reset,
    control,
    setValue,
    watch,
    formState: { isDirty, errors: formErrors },
  } = useForm<IForm>({
    defaultValues: {
      name: testPlan.name,
      description: testPlan.description,
      started_at: dayjs(testPlan.started_at),
      due_date: dayjs(testPlan.due_date),
      parent: testPlan.parent ? testPlan.parent.id : null,
      test_cases: [],
    },
  })
  const testCasesWatch = watch("test_cases")

  const { data: tests, isLoading: isLoadingTestCases } = useGetTestPlanCasesQuery(
    {
      testPlanId: String(testPlan.id),
    },
    { skip: !isShow }
  )
  const [updateTestPlan, { isLoading: isLoadingUpdate }] = useUpdateTestPlanMutation()

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
    isLoading: isLoadingSearch,
    onSearch,
    onRowExpand,
    onClearSearch,
  } = useTestPlanCommonModal({ isShow })

  const {
    attachments,
    attachmentsIds,
    isLoading: isLoadingAttachments,
    setAttachments,
    onLoad,
  } = useAttachments<IForm>(control, Number(projectId))

  useEffect(() => {
    if (!isShow) return

    const ids = tests?.case_ids.map((i) => String(i)) ?? []
    reset({
      name: testPlan.name,
      description: testPlan.description,
      started_at: dayjs(testPlan.started_at),
      due_date: dayjs(testPlan.due_date),
      parent: testPlan.parent ? testPlan.parent.id : null,
      test_cases: ids,
    })

    setDateFrom(dayjs(testPlan.started_at))
    setDateTo(dayjs(testPlan.due_date))

    if (testPlan.parent) {
      setSelectedParent({ value: testPlan.parent.id, label: testPlan.parent.name })
    }
  }, [testPlan, tests, isShow])

  const onCloseModal = () => {
    setIsShow(false)
    setErrors(null)
    onClearSearch()
    reset()
  }

  const handleClose = () => {
    if (isLoadingTestCases) return

    if (isDirty) {
      showModal(onCloseModal)
      return
    }

    onCloseModal()
  }

  const onSubmit: SubmitHandler<IForm> = async (data) => {
    setErrors(null)
    const newTestCases = data.test_cases?.filter((item) => !item.startsWith("TS"))
    try {
      const newPlan = await updateTestPlan({
        id: testPlan.id,
        body: {
          ...data,
          due_date: dayjs(data.due_date).format("YYYY-MM-DDThh:mm"),
          started_at: dayjs(data.started_at).format("YYYY-MM-DDThh:mm"),
          parent: data.parent ?? null,
          test_cases: newTestCases,
        },
      }).unwrap()
      notification.success({
        message: t("Success"),
        closable: true,
        description: (
          <AlertSuccessChange
            id={String(testPlan.id)}
            action="updated"
            title={t("Test Plan")}
            link={`/projects/${projectId}/plans/${testPlan.id}`}
          />
        ),
      })
      onCloseModal()
      onSubmitCb?.(newPlan, testPlan)
    } catch (err) {
      onHandleError(err)
    }
  }

  const handleSelectTestPlan = (value: SelectData | null) => {
    setErrors({ parent: "" })
    if (value?.value === testPlan.id) {
      setErrors({ parent: t("Test Plan cannot be its own parent.") })
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
    errors,
    formErrors,
    control,
    selectedParent,
    searchText,
    treeData,
    expandedRowKeys,
    isDirty,
    isLoadingTestCases,
    isLoadingUpdate,
    isLoadingSearch,
    handleClose,
    handleRowExpand: onRowExpand,
    handleSubmitForm: handleSubmit(onSubmit),
    handleSearch: onSearch,
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
