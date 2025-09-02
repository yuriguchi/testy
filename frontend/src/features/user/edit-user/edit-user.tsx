import { EditOutlined } from "@ant-design/icons"
import { Button } from "antd"

import { useAppDispatch } from "app/hooks"

import { setUserModal, showEditUserModal } from "entities/user/model"

export const EditUser = ({ user }: { user: User }) => {
  const dispatch = useAppDispatch()

  const showUserDetails = () => {
    dispatch(setUserModal(user))
    dispatch(showEditUserModal())
  }

  return (
    <Button
      id={`show-user-details-${user.username}`}
      data-testid={`show-user-details-${user.username}`}
      icon={<EditOutlined />}
      shape="circle"
      onClick={showUserDetails}
    />
  )
}
