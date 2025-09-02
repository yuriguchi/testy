import { AttachmentDropFiles } from "./drop-files"
import { AttachmentField } from "./field"
import { AttachmentItem } from "./item"
import { AttachmentList } from "./list"

const Attachment = ({ children }: { children: React.ReactNode }) => <>{children}</>

Attachment.Field = AttachmentField
Attachment.Item = AttachmentItem
Attachment.List = AttachmentList
Attachment.DropFiles = AttachmentDropFiles

export { Attachment }
