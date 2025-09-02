import { useTranslation } from "react-i18next"

import { AttachmentItem } from "./item"

interface AttachmentListProps {
  attachments: IAttachment[]
  handleAttachmentRemove?: (fileId: number) => void
  isShowNoAttachment?: boolean
}

export const AttachmentList = ({
  attachments,
  isShowNoAttachment = true,
  handleAttachmentRemove,
}: AttachmentListProps) => {
  const { t } = useTranslation()
  if (attachments.length === 0 && isShowNoAttachment) return <p>{t("No attachments")}</p>

  return (
    <>
      {attachments.map((attachment, index) => (
        <AttachmentItem
          key={`${attachment.id}-${index}`}
          handleAttachmentRemove={handleAttachmentRemove}
          attachment={attachment}
        />
      ))}
    </>
  )
}
