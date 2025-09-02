import { Button, Modal, notification } from "antd"
import { useDeleteCommentMutation } from "entities/comments/api"
import { useTranslation } from "react-i18next"

import { initInternalError } from "shared/libs"

export const DeleteComment = ({ commentId }: { commentId: number }) => {
  const { t } = useTranslation()
  const [deleteComment] = useDeleteCommentMutation()

  const handleDelete = async () => {
    try {
      await deleteComment(commentId).unwrap()
      notification.success({
        message: t("Success"),
        closable: true,
        description: t("Comment deleted successfully"),
      })
    } catch (err: unknown) {
      initInternalError(err)
    }
  }

  return (
    <Button
      id="delete-comment"
      type="link"
      style={{
        border: "none",
        padding: 0,
        height: "auto",
        lineHeight: 1,
      }}
      onClick={() => {
        Modal.confirm({
          title: t("Do you want to delete this comment?"),
          okText: t("Delete"),
          cancelText: t("Cancel"),
          onOk: handleDelete,
          okButtonProps: { "data-testid": "delete-comment-button-confirm" },
          cancelButtonProps: { "data-testid": "delete-comment-button-cancel" },
        })
      }}
    >
      <span style={{ textDecoration: "underline" }}>{t("Delete")}</span>
    </Button>
  )
}
