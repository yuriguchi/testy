import { notification } from "antd"
import { UploadChangeParam, UploadFile } from "antd/lib/upload"
import { Mutex } from "async-mutex"
import type { UploadRequestError, UploadRequestOption } from "rc-upload/lib/interface"
import { useEffect, useState } from "react"
import { Control, FieldValues, useFieldArray } from "react-hook-form"

import { useCreateAttachmentMutation } from "entities/attachment/api"

import { initInternalError } from "shared/libs"

const mutex = new Mutex()

interface UploadFileExtend<T> extends UploadFile<T> {
  id?: number
  link?: string
}

// prettier-ignore
export const useAttachments = <T, >(
  control: Control<T & FieldValues, unknown>,
  projectId: number
) => {
  const [attachments, setAttachments] = useState<IAttachmentWithUid[]>([])
  const [createAttachment, { isLoading }] = useCreateAttachmentMutation()
  const {
    fields: attachmentsIds,
    append: appendAttachmentIds,
    remove: removeAttachmentIds,
  } = useFieldArray({ name: "attachments", control: control as Control<FieldValues> })

  useEffect(() => {
    removeAttachmentIds()
    appendAttachmentIds(attachments.map(({ id }: IAttachmentWithUid) => id))
  }, [attachments])

  const onRemove = (fileId: number) => {
    setAttachments(attachments.filter(({ id }: IAttachment) => id !== fileId))
  }

  const onLoad = async (options: UploadRequestOption<unknown>) => {
    const { onSuccess, onError, file } = options
    const fileFormat = file as UploadFileExtend<IAttachmentWithUid[]>

    if (!projectId || !onSuccess || !onError) {
      notification.error({
        message: "Error!",
        description: "ProjectId is undefined",
      })
      return
    }

    const fmData = new FormData()
    fmData.append("file", file)
    fmData.append("project", String(projectId))

    await mutex.waitForUnlock()
    const release = await mutex.acquire()

    try {
      const response = await createAttachment(fmData).unwrap()
      fileFormat.id = response[0].id
      fileFormat.link = response[0].link
      onSuccess("Ok")
    } catch (err) {
      const error = err as UploadRequestError
      initInternalError(err)
      onError(error)
    } finally {
      release()
    }
  }

  const onChange = (info: UploadChangeParam<UploadFileExtend<IAttachmentWithUid[]>>) => {
    const fileList = info.fileList as IAttachmentWithUid[]
    setAttachments(fileList)
  }

  const onReset = () => {
    removeAttachmentIds()
    setAttachments([])
  }

  return {
    onLoad,
    onRemove,
    onChange,
    setAttachments,
    removeAttachmentIds,
    onReset,
    attachmentsIds,
    attachments,
    isLoading,
  }
}
