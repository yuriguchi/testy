import { notification } from "antd"
import { useEffect, useMemo, useState } from "react"
import { SubmitHandler, useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"
import { useParams } from "react-router-dom"

import { useCreateLabelMutation, useUpdateLabelMutation } from "entities/label/api"

import { useErrors } from "shared/hooks"

interface ErrorData {
  name?: string
  type?: string
}

export interface UseCreateEditLabelModalProps {
  mode: ModalMode
  isShow: boolean
  setIsShow: (isShow: boolean) => void
  label?: Label
}

export const useCreateEditLabelModal = ({
  mode,
  label,
  setIsShow,
  isShow,
}: UseCreateEditLabelModalProps) => {
  const { t } = useTranslation()
  const { projectId } = useParams<ParamProjectId>()

  const [createLabel, { isLoading: isLoadingCreating }] = useCreateLabelMutation()
  const [updateLabel, { isLoading: isLoadingUpdating }] = useUpdateLabelMutation()

  const [errors, setErrors] = useState<ErrorData | null>(null)
  const { onHandleError } = useErrors<ErrorData>(setErrors)
  const {
    handleSubmit,
    reset,
    control,
    setValue,
    formState: { isDirty },
  } = useForm<LabelUpdate>({
    defaultValues: {
      name: label?.name ?? "",
      type: 0,
    },
  })

  const onSubmit: SubmitHandler<LabelUpdate> = async (data) => {
    setErrors(null)

    try {
      if (mode === "edit" && label && projectId) {
        await updateLabel({
          id: Number(label.id),
          body: data,
        }).unwrap()
      } else {
        await createLabel({ ...data, project: Number(projectId) }).unwrap()
      }
      notification.success({
        message: t("Success"),
        closable: true,
        description:
          mode === "edit" ? t("Label updated successfully") : t("Label created successfully"),
      })
      handleCloseModal()
    } catch (err) {
      onHandleError(err)
    }
  }

  const handleCloseModal = () => {
    setErrors(null)
    reset()
    setIsShow(false)
  }

  const handleCancel = () => {
    if (!isLoadingCreating || !isLoadingUpdating) {
      handleCloseModal()
    }
  }

  const title = useMemo(() => {
    if (mode === "create" || !label) {
      return t("Create label")
    }

    // eslint-disable-next-line @typescript-eslint/restrict-template-expressions
    return `${t("Edit label")} ${label.name}`
  }, [mode, label])

  // use effect for edit modal
  useEffect(() => {
    if (!isShow || mode !== "edit" || !label) return

    setValue("name", label.name)
    setValue("type", label.type)
  }, [mode, label])

  return {
    title,
    isShow,
    control,
    errors,
    isLoading: isLoadingCreating || isLoadingUpdating,
    isDirty,
    handleCancel,
    handleSubmitForm: handleSubmit(onSubmit),
  }
}
