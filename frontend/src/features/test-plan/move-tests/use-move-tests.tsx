import { useEffect, useState } from "react"
import { useForm } from "react-hook-form"

import { initInternalError } from "shared/libs"

interface FormPlan {
  plan: SelectData | null
}

export interface MoveTestsProps {
  isLoading?: boolean
  onSubmit: (plan: number) => Promise<void>
}

export const useMoveTestsModal = ({ onSubmit }: MoveTestsProps) => {
  const [isShow, setIsShow] = useState(false)
  const [errors, setErrors] = useState<string[]>([])
  const [selectedPlan, setSelectedPlan] = useState<SelectData | null>(null)

  const {
    handleSubmit,
    reset,
    control,
    formState: { isDirty, errors: formErrors },
    setValue,
  } = useForm<FormPlan>({
    defaultValues: {
      plan: null,
    },
  })

  const onHandleError = (err: unknown) => {
    initInternalError(err)
  }

  const handleCancel = () => {
    setIsShow(false)
    setErrors([])
    reset()
  }

  const handleShow = () => {
    setIsShow(true)
  }

  const handleSave = async ({ plan }: FormPlan) => {
    if (!plan?.value) {
      return
    }

    try {
      await onSubmit(plan.value)
      handleCancel()
    } catch (e) {
      onHandleError(e)
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
      plan: null,
    })
    setSelectedPlan(null)
  }, [isShow])

  return {
    isShow,
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
  }
}
