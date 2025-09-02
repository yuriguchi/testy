import { DeleteOutlined } from "@ant-design/icons"
import { Button, Modal, notification } from "antd"
import { useDeleteCustomAttributeMutation } from "entities/custom-attribute/api"
import { useTranslation } from "react-i18next"

import { initInternalError } from "shared/libs"

interface Props {
  attributeId: Id
}

export const DeleteCustomAttribute = ({ attributeId }: Props) => {
  const { t } = useTranslation()
  const [deleteAttribute] = useDeleteCustomAttributeMutation()

  const handleDeleteAttribute = (AttributeId: Id) => {
    Modal.confirm({
      title: t("Do you want to delete these attribute?"),
      okText: t("Delete"),
      cancelText: t("Cancel"),
      onOk: async () => {
        try {
          await deleteAttribute(AttributeId).unwrap()
          notification.success({
            message: t("Success"),
            closable: true,
            description: t("Attribute deleted successfully"),
          })
        } catch (err: unknown) {
          initInternalError(err)
        }
      },
      okButtonProps: { "data-testid": "delete-attribute-button-confirm" },
      cancelButtonProps: { "data-testid": "delete-attribute-button-cancel" },
    })
  }

  return (
    <Button
      id={`delete-custom-attribute-${attributeId}`}
      icon={<DeleteOutlined />}
      shape="circle"
      danger
      onClick={() => handleDeleteAttribute(Number(attributeId))}
    />
  )
}
