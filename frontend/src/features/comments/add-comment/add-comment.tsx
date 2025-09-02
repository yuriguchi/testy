import { UploadOutlined } from "@ant-design/icons"
import { Alert, Button, Upload } from "antd"
import { useTranslation } from "react-i18next"

import { Attachment, TextArea } from "shared/ui"

import { useAddComment } from "./use-add-comment"

interface Props {
  model: Models
  object_id: string
  setIsShowAdd: (value: boolean) => void
}

export const AddComment = ({ model, object_id, setIsShowAdd }: Props) => {
  const {
    errors,
    comment,
    attachments,
    isLoadingAddComment,
    isLoadingCreateAttachment,
    setComment,
    handleAddClick,
    handleAttachmentRemove,
    handleLoadAttachmentChange,
    handleAttachmentLoad,
  } = useAddComment({ setIsShowAdd, model, object_id })
  const { t } = useTranslation()
  return (
    <div style={{ marginTop: 12, gap: 12, display: "flex", flexDirection: "column" }}>
      <TextArea
        id="add-comments-text-area"
        style={{ fontSize: 13 }}
        rows={4}
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        placeholder={t("Type a comment")}
        autoFocus
      />
      {!!errors?.errors?.length && <Alert description={errors.errors} type="error" />}
      <Attachment.List
        handleAttachmentRemove={handleAttachmentRemove}
        attachments={attachments}
        isShowNoAttachment={false}
      />
      <div style={{ display: "flex", alignItems: "center" }}>
        <Upload
          showUploadList={false}
          onChange={handleLoadAttachmentChange}
          customRequest={handleAttachmentLoad}
        >
          <Button icon={<UploadOutlined />}>{t("Upload file")}</Button>
        </Upload>
        <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginLeft: "auto" }}>
          <Button
            id="add-comment-btn"
            type="primary"
            onClick={handleAddClick}
            loading={isLoadingAddComment || isLoadingCreateAttachment}
            disabled={!comment.length && !attachments.length}
          >
            {t("Add")}
          </Button>
          <Button id="cancel-comment-btn" onClick={() => setIsShowAdd(false)} type="text">
            {t("Cancel")}
          </Button>
        </div>
      </div>
    </div>
  )
}
