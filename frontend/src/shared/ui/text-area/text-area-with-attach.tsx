import { PictureOutlined } from "@ant-design/icons"
import { Button, Input, Upload } from "antd"
import { TextAreaProps } from "antd/lib/input/TextArea"
import type { UploadRequestOption } from "rc-upload/lib/interface"
import { useEffect, useRef, useState } from "react"
import { UseFormSetValue } from "react-hook-form"

import { MarkdownViewer, MarkdownViewerTabs } from ".."
import styles from "./styles.module.css"

interface TSTextAreaProps {
  uploadId?: string
  textAreaId?: string
  fieldProps: TextAreaProps
  stateAttachments: {
    attachments: IAttachmentWithUid[]
    setAttachments: React.Dispatch<React.SetStateAction<IAttachmentWithUid[]>>
  }
  customRequest: (options: UploadRequestOption<unknown>) => Promise<void>
  // TODO fix it
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  setValue: UseFormSetValue<any>
}

type ViewTab = "md" | "view"

export const TextAreaWithAttach = ({
  uploadId = "text-area-with-attach",
  textAreaId = "text-area-with-attach",
  fieldProps,
  stateAttachments,
  customRequest,
  setValue,
}: TSTextAreaProps) => {
  const [tab, setTab] = useState<ViewTab>("md")
  const [textAreaHeight, setTextAreaHeight] = useState<number | null>(null)
  const { attachments, setAttachments } = stateAttachments
  const uploadRef = useRef(null)

  // TODO need refactoring
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const onChange = (info: any) => {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-argument, @typescript-eslint/no-unsafe-member-access
    setAttachments(info.fileList)

    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access
    const { status } = info.file
    if (status === "done" && fieldProps.name) {
      // eslint-disable-next-line @typescript-eslint/restrict-plus-operands, @typescript-eslint/no-unsafe-member-access, @typescript-eslint/restrict-template-expressions
      const value = `${fieldProps.value ?? ""}![](${info.file.link})`
      setValue(fieldProps.name, value, {
        shouldDirty: true,
      })
    }
  }

  const handlePaste = (e: React.ClipboardEvent<HTMLTextAreaElement>) => {
    const { files } = e.clipboardData
    if (!files.length) return
    // @ts-ignore
    // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access, @typescript-eslint/no-unsafe-call
    uploadRef.current.upload.uploader.uploadFiles(files)
  }

  const handleTabClick = (newTab: ViewTab) => {
    setTab(newTab)
  }

  useEffect(() => {
    const el = document.querySelector(`#${textAreaId}`)

    function textAreaResize() {
      if (!el || el.clientHeight === 0) return
      setTextAreaHeight(el?.clientHeight ?? 0)
    }

    let resizeObserver: ResizeObserver
    if (el) {
      resizeObserver = new ResizeObserver(textAreaResize)
      resizeObserver.observe(el)
    }
    return () => resizeObserver?.disconnect()
  }, [textAreaId])

  return (
    <>
      <Input.TextArea
        id={textAreaId}
        style={{
          fontSize: 13,
          display: tab === "md" ? "inline-block" : "none",
          ...fieldProps.style,
        }}
        rows={4}
        {...fieldProps}
        onPasteCapture={handlePaste}
      />
      <MarkdownViewer
        tab={tab}
        textAreaHeight={textAreaHeight}
        value={fieldProps.value as string}
      />
      <div id={`${textAreaId}-bottom`} className={styles.row}>
        <MarkdownViewerTabs id={textAreaId} tab={tab} handleTabClick={handleTabClick} />
        <Upload
          ref={uploadRef}
          id={`${uploadId}-upload-attachment-input`}
          fileList={attachments}
          customRequest={customRequest}
          onChange={onChange}
          name="file"
          multiple
          showUploadList={false}
        >
          <Button
            id={`${uploadId}-upload-attachment-button`}
            icon={<PictureOutlined />}
            size={"small"}
            type="link"
            className={styles.pictureIcon}
          />
        </Upload>
      </div>
    </>
  )
}
