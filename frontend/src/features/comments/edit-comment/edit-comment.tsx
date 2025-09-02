import { UploadOutlined } from "@ant-design/icons"
import { Button, Modal, Upload } from "antd"
import { useTranslation } from "react-i18next"

import { Attachment, TextArea } from "shared/ui"

import { useEditComment } from "./use-edit-comment"

interface Props {
  comment: CommentType
}

export const EditComment = ({ comment }: Props) => {
  const { t } = useTranslation()
  const {
    isShow,
    isLoading,
    commentValue,
    attachments,
    handleShow,
    handleClose,
    handleSaveClick,
    handleChangeComment,
    handleAttachmentRemove,
    handleAttachmentLoad,
    handleLoadAttachmentChange,
  } = useEditComment(comment)

  return (
    <>
      <Button
        id="edit-comment"
        onClick={handleShow}
        type="link"
        style={{
          border: "none",
          padding: 0,
          height: "auto",
          lineHeight: 1,
        }}
      >
        <span style={{ textDecoration: "underline" }}>{t("Edit")}</span>
      </Button>
      <Modal
        className="edit-comment-modal"
        title={t("Edit comment")}
        open={isShow}
        onCancel={handleClose}
        footer={[
          <Button key="back" onClick={handleClose} type="text">
            {t("Cancel")}
          </Button>,
          <Button
            key="submit"
            type="primary"
            onClick={handleSaveClick}
            loading={isLoading}
            disabled={!commentValue.length}
          >
            {t("Save")}
          </Button>,
        ]}
      >
        <TextArea
          id="edit-comments-text-area"
          style={{ fontSize: 13 }}
          rows={4}
          value={commentValue}
          onChange={handleChangeComment}
        />
        <div style={{ marginTop: 12 }}>
          <div style={{ marginBottom: attachments.length ? 12 : 0 }}>
            <Upload
              showUploadList={false}
              onChange={handleLoadAttachmentChange}
              customRequest={handleAttachmentLoad}
            >
              <Button icon={<UploadOutlined />}>{t("Upload file")}</Button>
            </Upload>
          </div>
          <Attachment.List
            handleAttachmentRemove={handleAttachmentRemove}
            attachments={attachments}
            isShowNoAttachment={false}
          />
        </div>
      </Modal>
    </>
  )
}
