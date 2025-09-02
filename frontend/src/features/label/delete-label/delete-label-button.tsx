import { DeleteOutlined } from "@ant-design/icons"
import { Button, Modal, notification } from "antd"
import { useTranslation } from "react-i18next"

import { useDeleteLabelMutation } from "entities/label/api"

import { initInternalError } from "shared/libs"

interface Props {
  label: Label
}

export const DeleteLabelButton = ({ label }: Props) => {
  const { t } = useTranslation()
  const [deleteLabel] = useDeleteLabelMutation()

  const handleDeleteLabel = () => {
    Modal.confirm({
      title: t("Do you want to delete these label?"),
      okText: t("Delete"),
      cancelText: t("Cancel"),
      onOk: async () => {
        try {
          await deleteLabel(Number(label.id)).unwrap()
          notification.success({
            message: t("Success"),
            closable: true,
            description: t("Label deleted successfully"),
          })
        } catch (err: unknown) {
          initInternalError(err)
        }
      },
      okButtonProps: { "data-testid": "delete-label-button-confirm" },
      cancelButtonProps: { "data-testid": "delete-label-button-cancel" },
    })
  }

  return (
    <Button
      id={`${label.name}-delete-label-button`}
      icon={<DeleteOutlined />}
      shape="circle"
      danger
      onClick={handleDeleteLabel}
    />
  )
}
