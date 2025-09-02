import { notification } from "antd"
import { useEffect, useState } from "react"
import { SubmitHandler, useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"

import { useAppDispatch, useAppSelector } from "app/hooks"

import { useCreateUserMutation, useUpdateUserMutation } from "entities/user/api"
import {
  hideModal,
  selectModalIsEditMode,
  selectModalIsShow,
  selectUserModal,
} from "entities/user/model"

import { useErrors, useShowModalCloseConfirm } from "shared/hooks"

interface Inputs {
  username: string
  email: string
  first_name: string
  last_name: string
  password: string
  confirm: string
  is_active: boolean
  is_superuser: boolean
}

interface ErrorData {
  username?: string
  email?: string
  password?: string
  confirm?: string
  first_name?: string
  last_name?: string
  is_active?: string
  is_superuser?: string
}

export const useUserModal = () => {
  const { t } = useTranslation()
  const { showModal } = useShowModalCloseConfirm()
  const dispatch = useAppDispatch()
  const isShow = useAppSelector(selectModalIsShow)
  const isEditMode = useAppSelector(selectModalIsEditMode)
  const modalUser = useAppSelector(selectUserModal)
  const [errors, setErrors] = useState<ErrorData | null>(null)
  const {
    handleSubmit,
    reset,
    control,
    setValue,
    watch,
    getValues,
    formState: { isDirty },
  } = useForm<Inputs>({
    defaultValues: {
      email: modalUser?.email,
      first_name: modalUser?.first_name,
      last_name: modalUser?.last_name,
      password: "",
      confirm: "",
      username: modalUser?.username,
      is_active: true,
      is_superuser: false,
    },
  })
  const [createUser, { isLoading }] = useCreateUserMutation()
  const [updateUser] = useUpdateUserMutation()
  const { onHandleError } = useErrors(setErrors)

  const password = watch("password")
  const passwordConfirm = watch("confirm")
  const isActive = watch("is_active")
  const isAdmin = watch("is_superuser")

  useEffect(() => {
    const [formPassword, formPasswordConfirm] = getValues(["password", "confirm"])
    if (formPassword !== formPasswordConfirm && formPassword && formPasswordConfirm) {
      setErrors({ confirm: t("The passwords that you entered do not match!") })
    } else {
      setErrors(null)
    }
  }, [password, passwordConfirm])

  useEffect(() => {
    if (isEditMode && modalUser) {
      setValue("username", modalUser.username)
      setValue("email", modalUser.email)
      setValue("first_name", modalUser.first_name)
      setValue("last_name", modalUser.last_name)
      setValue("is_active", modalUser.is_active)
      setValue("is_superuser", modalUser.is_superuser)
    } else {
      setValue("is_active", true)
      setValue("is_superuser", true)
    }
  }, [isEditMode, modalUser])

  const onSubmit: SubmitHandler<Inputs> = async (data) => {
    const [formPassword, confirm, username, email] = getValues([
      "password",
      "confirm",
      "username",
      "email",
    ])

    const isShortChange = isEditMode && !formPassword && !confirm
    const fields = isShortChange
      ? { username, email }
      : { password: formPassword, confirm, username, email }

    const newErrors: ErrorData = {} as ErrorData
    Object.keys(fields).forEach((key) => {
      const fieldName = key as keyof typeof fields
      if (!fields[fieldName]) {
        newErrors[fieldName] = t("This field can not be empty!")
      }
    })

    if (formPassword !== confirm && formPassword && confirm) {
      newErrors.confirm = t("The passwords that you entered do not match!")
    }

    if (Object.keys(newErrors).length) {
      setErrors(newErrors)
      return
    }
    setErrors(null)

    if (isShortChange) {
      //@ts-ignore
      delete data.password
      //@ts-ignore
      delete data.confirm
    }

    try {
      isEditMode && modalUser
        ? await updateUser({ id: modalUser.id, body: data }).unwrap()
        : await createUser({
            ...data,
          }).unwrap()
      onCloseModal()
      notification.success({
        message: t("Success"),
        closable: true,
        description: isEditMode ? t("User updated successfully") : t("User created successfully"),
      })
    } catch (err) {
      onHandleError(err)
    }
  }

  const onCloseModal = () => {
    dispatch(hideModal())
    setErrors(null)
    reset()
  }

  const handleCancel = () => {
    if (isLoading) return

    if (isDirty) {
      showModal(onCloseModal)
      return
    }

    onCloseModal()
  }

  const title = isEditMode ? `${t("Edit User")} '${modalUser?.username}'` : t("Create User")

  return {
    title,
    isShow,
    isEditMode,
    isLoading,
    isActive,
    isAdmin,
    isDirty,
    errors,
    control,
    handleCancel,
    handleSubmitForm: handleSubmit(onSubmit),
  }
}
