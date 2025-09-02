import { UploadChangeParam } from "antd/es/upload"
import Dragger from "antd/es/upload/Dragger"
import { UploadFile } from "antd/lib"
import type { UploadRequestOption } from "rc-upload/lib/interface"
import { useTranslation } from "react-i18next"

import { AttachmentList } from "./list"

interface UploadFileExtend<T> extends UploadFile<T> {
  id?: number
  link?: string
}

interface Props {
  onRemove: (fileId: number) => void
  onLoad: (options: UploadRequestOption<unknown>) => Promise<void>
  onChange: (info: UploadChangeParam<UploadFileExtend<IAttachmentWithUid[]>>) => void
  attachments: IAttachmentWithUid[]
  attachmentsIds: Record<"id", string>[]
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  register: any
  idInput?: string
}

export const AttachmentDropFiles = ({
  attachments,
  attachmentsIds,
  onChange,
  onLoad,
  onRemove,
  register,
  idInput,
}: Props) => {
  const { t } = useTranslation()
  return (
    <>
      <AttachmentList handleAttachmentRemove={onRemove} attachments={attachments} />
      {attachmentsIds.map((field, index) => (
        <input
          type="hidden"
          key={field.id}
          // eslint-disable-next-line @typescript-eslint/no-unsafe-call
          {...register(`attachments.${index}`)}
        />
      ))}
      <Dragger
        name="file"
        multiple
        showUploadList={false}
        customRequest={onLoad}
        onChange={onChange}
        fileList={attachments}
        height={80}
        data-testid={idInput}
      >
        <p className="ant-upload-text">{t("Drop files here to attach, or click to browse")}</p>
      </Dragger>
    </>
  )
}
