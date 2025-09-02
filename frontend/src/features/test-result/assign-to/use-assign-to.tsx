import { useEffect } from "react"

import { useAppDispatch, useAppSelector } from "app/hooks"

import { useUpdateTestMutation } from "entities/test/api"
import { selectDrawerTest, setDrawerTest } from "entities/test/model/slice"

import { useAssignToCommon } from "./use-assign-to-common"

interface Props {
  onSuccess?: () => void
}

export const useAssignTo = ({ onSuccess }: Props) => {
  const activeTest = useAppSelector(selectDrawerTest)
  const dispatch = useAppDispatch()
  const [updateTest, { isLoading: isLoadingUpdateTest }] = useUpdateTestMutation()

  const assignRequest = async (assignUserId: string) => {
    if (!activeTest) return

    const result = await updateTest({
      id: activeTest.id,
      body: {
        assignee: assignUserId,
      },
    }).unwrap()
    dispatch(setDrawerTest(result))
    onSuccess?.()
  }

  const {
    isOpenModal,
    errors,
    isDirty,
    me,
    handleClose,
    handleOpenAssignModal,
    handleAssignUserChange,
    handleAssignUserClear,
    handleAssignToMe,
    setSelectedUser,
    handleSubmitForm,
    selectedUser,
  } = useAssignToCommon({ onSubmit: assignRequest })

  useEffect(() => {
    if (!activeTest?.assignee) return
    setSelectedUser({
      label: String(activeTest.assignee_username),
      value: Number(activeTest.assignee),
    })
  }, [activeTest])

  return {
    activeTest,
    isOpenModal,
    errors,
    isDirty,
    isLoadingUpdateTest,
    me,
    selectedUser,
    handleClose,
    handleSubmitForm,
    handleOpenAssignModal,
    handleAssignUserChange,
    handleAssignUserClear,
    handleAssignToMe,
  }
}
