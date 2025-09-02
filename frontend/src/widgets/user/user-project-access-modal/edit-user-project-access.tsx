import { EditOutlined } from "@ant-design/icons"
import { Button } from "antd"
import { openRoleModal } from "entities/roles/model"

import { useAppDispatch } from "app/hooks"

interface Props {
  user: UserWithRoles
}

export const EditUserProjectAccess = ({ user }: Props) => {
  const dispatch = useAppDispatch()
  const handleClick = () => {
    dispatch(openRoleModal({ mode: "edit", user }))
  }
  return (
    <Button
      data-testid={`${user.username}-edit-user-project-access`}
      icon={<EditOutlined />}
      shape="circle"
      onClick={handleClick}
    />
  )
}
