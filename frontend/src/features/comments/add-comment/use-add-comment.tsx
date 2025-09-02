import { notification } from "antd"
import { useAddCommentMutation } from "entities/comments/api"
import { useContext, useState } from "react"
import { useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"

import { useAttachments } from "entities/attachment/model"

import { ProjectContext } from "pages/project"

import { useErrors } from "shared/hooks"

interface Props {
  model: Models
  object_id: string
  setIsShowAdd: (value: boolean) => void
}

export const useAddComment = ({ setIsShowAdd, model, object_id }: Props) => {
  const { t } = useTranslation()
  const { project } = useContext(ProjectContext)!
  const [comment, setComment] = useState("")
  const [errors, setErrors] = useState<{ errors: string[] } | null>(null)
  const { onHandleError } = useErrors<{ errors: string[] }>(setErrors)
  const [addComment, { isLoading: isLoadingAddComment }] = useAddCommentMutation()
  const { control } = useForm()
  const {
    attachments,
    isLoading: isLoadingCreateAttachment,
    onChange: handleLoadAttachmentChange,
    onRemove: handleAttachmentRemove,
    onLoad: handleAttachmentLoad,
  } = useAttachments(control, project.id)

  const handleAddClick = async () => {
    const attachmentsIds = attachments.map((attach) => String(attach.id))
    try {
      await addComment({ model, object_id, content: comment, attachments: attachmentsIds }).unwrap()
      notification.success({
        message: t("Success"),
        closable: true,
      })
      setComment("")
      setIsShowAdd(false)
    } catch (err: unknown) {
      onHandleError(err)
    }
  }

  return {
    isLoadingAddComment,
    isLoadingCreateAttachment,
    attachments,
    comment,
    errors,
    handleAddClick,
    handleAttachmentRemove,
    handleAttachmentLoad,
    handleLoadAttachmentChange,
    setComment,
  }
}
