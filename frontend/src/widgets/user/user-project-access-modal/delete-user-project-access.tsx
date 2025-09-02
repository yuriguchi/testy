import { DeleteOutlined } from "@ant-design/icons"
import { Button, Modal, notification } from "antd"
import { useUnassignRoleMutation } from "entities/roles/api"
import { selectRoleOnSuccess } from "entities/roles/model"
import { useTranslation } from "react-i18next"
import { useParams } from "react-router-dom"

import { useAppSelector } from "app/hooks"

import { initInternalError } from "shared/libs"

interface Props {
  user: User
}

export const DeleteUsetProjectAccess = ({ user }: Props) => {
  const { t } = useTranslation()
  const [unassignUser] = useUnassignRoleMutation()
  const onSuccess = useAppSelector(selectRoleOnSuccess)
  const { projectId } = useParams<ParamProjectId>()
  const handleModalConfirm = async () => {
    try {
      await unassignUser({
        user: user.id,
        project: Number(projectId),
      }).unwrap()

      notification.success({
        message: t("Success"),
        closable: true,
        description: t("User access deleted successfully"),
      })

      onSuccess?.()
    } catch (err: unknown) {
      initInternalError(err)
    }
  }

  return (
    <Button
      data-testid={`${user.username}-delete-user-project-access`}
      icon={<DeleteOutlined />}
      shape="circle"
      danger
      onClick={() => {
        Modal.confirm({
          title: t("Do you want to delete user from project?"),
          okText: t("Delete"),
          cancelText: t("Cancel"),
          onOk: handleModalConfirm,
          okButtonProps: { "data-testid": "delete-user-button-confirm" },
          cancelButtonProps: { "data-testid": "delete-user-button-cancel" },
        })
      }}
    />
  )
}
