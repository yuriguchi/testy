import { notification } from "antd"
import {
  useAssignRoleMutation,
  useGetRolesQuery,
  useUpdateAssignedRoleMutation,
} from "entities/roles/api"
import {
  closeRoleModal,
  selectIsRoleModalOpen,
  selectRoleModalMode,
  selectRoleOnSuccess,
  selectRoleUser,
} from "entities/roles/model"
import { useEffect, useState } from "react"
import { SubmitHandler, useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"
import { useParams } from "react-router-dom"

import { useAppDispatch, useAppSelector } from "app/hooks"

import { UserSearchOption } from "entities/user/ui"

import { useErrors } from "shared/hooks"

interface UpdateData {
  user: string
  roles: number[]
}

export const useUserProjectAccessModal = () => {
  const { t } = useTranslation()
  const { projectId } = useParams<ParamProjectId>()
  const [selectedUser, setSelectedUser] = useState<SelectData | null>(null)
  const isOpenned = useAppSelector(selectIsRoleModalOpen)
  const mode = useAppSelector(selectRoleModalMode)
  const user = useAppSelector(selectRoleUser)
  const dispatch = useAppDispatch()
  const isEditMode = mode === "edit"
  const onSuccess = useAppSelector(selectRoleOnSuccess)

  const { data: roles, isLoading } = useGetRolesQuery({})

  const {
    handleSubmit,
    reset,
    setValue,
    control,
    formState: { isDirty },
  } = useForm<UpdateData>()
  const [errors, setErrors] = useState<Partial<UpdateData> | null>(null)
  const { onHandleError } = useErrors<Partial<UpdateData>>(setErrors)
  const [assignUser] = useAssignRoleMutation()
  const [updateUserAssign] = useUpdateAssignedRoleMutation()

  useEffect(() => {
    if (user) {
      setValue("user", String(user.id), { shouldDirty: false })
      setSelectedUser({ label: <UserSearchOption user={user} />, value: user.id })
      setValue(
        "roles",
        user.roles.map((role) => role.id),
        { shouldDirty: false }
      )
    } else {
      setSelectedUser(null)
    }
  }, [user])

  const handleSubmitForm = async (data: UpdateData) => {
    try {
      if (isEditMode) {
        if (!user) {
          throw new Error("User not found")
        }
        await updateUserAssign({
          user: user.id,
          roles: data.roles.map(Number),
          project: Number(projectId),
        }).unwrap()
      } else {
        await assignUser({
          user: Number(data.user),
          roles: data.roles.map(Number),
          project: Number(projectId),
        }).unwrap()
      }

      const description = isEditMode
        ? t("User updated successfully")
        : t("User assigned successfully")
      notification.success({
        message: t("Success"),
        closable: true,
        description,
      })

      onSuccess?.()
      reset()
      handleClose()
      setSelectedUser(null)
    } catch (err) {
      onHandleError(err)
      notification.error({
        message: t("Error!"),
        description: t("User assign error"),
      })
    }
  }

  const handleClose = () => {
    dispatch(closeRoleModal())
    reset()
    setSelectedUser(null)
    setErrors(null)
  }

  const onSubmit: SubmitHandler<UpdateData> = (data) => {
    setErrors(null)
    handleSubmitForm(data)
  }

  const handleUserChange = (data?: SelectData) => {
    if (!data) return
    setSelectedUser(data)
    setValue("user", String(data.value) || "", { shouldDirty: true })
  }

  const handleUserClear = () => {
    setSelectedUser(null)
    setValue("user", "", { shouldDirty: true })
  }

  const title = mode === "create" ? t("Add user to project") : t("Edit user project access")

  return {
    isOpenned,
    errors,
    isDirty,
    selectedUser: selectedUser ?? undefined,
    handleClose,
    handleSubmitForm: handleSubmit(onSubmit),
    handleUserChange,
    handleUserClear,
    isLoading,
    roles: roles?.results ?? ([] as Role[]),
    control,
    title,
    isEditMode,
    mode,
    onSuccess,
  }
}
