import { notification } from "antd"
import dayjs, { Dayjs } from "dayjs"
import { useEffect, useState } from "react"
import { useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"

import { useСopyTestPlanMutation } from "entities/test-plan/api"

import { useDatepicker } from "shared/hooks"
import { initInternalError, isFetchBaseQueryError } from "shared/libs"
import { AlertSuccessChange } from "shared/ui"

interface FormPlanCopy {
  new_name: string
  startedAt: Dayjs | null
  dueDate: Dayjs | null
  keepAssignee: boolean
  plan: SelectData | null
}

interface ErrorData {
  plans: {
    plan: string[]
    new_name?: string[]
  }[]
}

interface Props {
  testPlan: TestPlan
  onSubmit?: (plan: TestPlan) => void
}

export const useTestPlanCopyModal = ({ testPlan, onSubmit }: Props) => {
  const { t } = useTranslation()
  const [isShow, setIsShow] = useState(false)
  const [errors, setErrors] = useState<string[]>([])
  const [copyTestPlan, { isLoading }] = useСopyTestPlanMutation()
  const [selectedPlan, setSelectedPlan] = useState<SelectData | null>(null)

  const {
    handleSubmit,
    reset,
    control,
    formState: { isDirty, errors: formErrors },
    setValue,
    watch,
  } = useForm<FormPlanCopy>({
    defaultValues: {
      new_name: `${testPlan.name}(Copy)`,
      startedAt: testPlan.started_at ? dayjs(testPlan.started_at) : null,
      dueDate: testPlan.due_date ? dayjs(testPlan.due_date) : null,
      keepAssignee: false,
      plan: null,
    },
  })
  const watchNewName = watch("new_name")

  const { setDateFrom, setDateTo, disabledDateFrom, disabledDateTo } = useDatepicker()

  const onHandleError = (err: unknown) => {
    if (isFetchBaseQueryError(err) && err?.status === 400) {
      const error = err.data as ErrorData
      const newNameErorrs = error.plans[0].new_name!
      setErrors(newNameErorrs)
    } else {
      initInternalError(err)
    }
  }

  const handleCancel = () => {
    setIsShow(false)
    setErrors([])
    reset()
  }

  const handleShow = () => {
    setIsShow(true)
  }

  const handleSave = async ({ new_name, plan, keepAssignee, startedAt, dueDate }: FormPlanCopy) => {
    if (!new_name.trim().length) {
      setErrors([t("New plan name is required")])
      return
    }

    try {
      const newPlan = await copyTestPlan({
        plans: [
          {
            plan: testPlan.id,
            new_name,
            started_at: startedAt?.toISOString(),
            due_date: dueDate?.toISOString(),
          },
        ],
        dst_plan: plan?.value,
        keep_assignee: keepAssignee,
      }).unwrap()
      notification.success({
        message: t("Success"),
        closable: true,
        description: (
          <AlertSuccessChange
            id={newPlan[0].id.toString()}
            link={`/projects/${newPlan[0].project}/plans/${newPlan[0].id}/`}
            action="copied"
            title={t("Test Plan")}
          />
        ),
      })
      handleCancel()
      onSubmit?.(newPlan[0])
    } catch (err) {
      onHandleError(err)
    }
  }

  const handleSelectPlan = (value?: SelectData | null) => {
    if (value) {
      setValue("plan", value, { shouldDirty: true })
      setSelectedPlan(value)
    }
  }

  useEffect(() => {
    reset({
      new_name: `${testPlan.name}(Copy)`,
      startedAt: testPlan.started_at ? dayjs(testPlan.started_at) : null,
      dueDate: testPlan.due_date ? dayjs(testPlan.due_date) : null,
      keepAssignee: false,
      plan: null,
    })
  }, [testPlan, isShow])

  return {
    isShow,
    isLoading,
    selectedPlan,
    handleSelectPlan,
    handleSave,
    handleShow,
    handleCancel,
    isDirty,
    errors,
    formErrors,
    control,
    handleSubmitForm: handleSubmit(handleSave),
    isDisabled: isLoading || !watchNewName,
    setDateFrom,
    setDateTo,
    disabledDateFrom,
    disabledDateTo,
  }
}
