import { notification } from "antd"
import { MeContext } from "processes"
import { useContext, useState } from "react"
import { SubmitHandler, useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"

import { useErrors } from "shared/hooks"

interface Props {
  onSubmit: (id: string) => Promise<void>
}

export interface UpdateData {
  assignUserId: string
}

export const useAssignToCommon = ({ onSubmit }: Props) => {
  const { t } = useTranslation()
  const { me } = useContext(MeContext)

  const [selectedUser, setSelectedUser] = useState<SelectData | null>(null)

  const [isOpenModal, setIsOpenModal] = useState(false)
  const {
    handleSubmit,
    reset,
    setValue,
    formState: { isDirty },
  } = useForm<UpdateData>()
  const [errors, setErrors] = useState<Partial<UpdateData> | null>(null)
  const { onHandleError } = useErrors<Partial<UpdateData>>(setErrors)

  const handleClose = () => {
    setIsOpenModal(false)
    reset()
  }

  const handleOpenAssignModal = () => {
    setIsOpenModal(true)
  }

  const performRequest = async (id: string) => {
    setErrors(null)
    try {
      await onSubmit(id)
      handleClose()

      notification.success({
        message: t("Success"),
        closable: true,
        description: t("User assigned successfully"),
      })
    } catch (err) {
      onHandleError(err)
    }
  }

  const handleAssignToMe = () => {
    if (!me) return

    performRequest(String(me.id))
  }

  const onSubmitHandler: SubmitHandler<UpdateData> = (data) => {
    performRequest(data.assignUserId)
  }

  const handleAssignUserChange = (data?: SelectData) => {
    if (!data) return
    setSelectedUser(data)
    setValue("assignUserId", String(data.value) || "", { shouldDirty: true })
  }

  const handleAssignUserClear = () => {
    setSelectedUser(null)
    setValue("assignUserId", "", { shouldDirty: true })
  }

  return {
    isOpenModal,
    errors,
    isDirty,
    me,
    selectedUser: selectedUser ?? undefined,
    handleClose,
    handleSubmitForm: handleSubmit(onSubmitHandler),
    handleOpenAssignModal,
    handleAssignUserChange,
    handleAssignUserClear,
    handleAssignToMe,
    setSelectedUser,
  }
}
