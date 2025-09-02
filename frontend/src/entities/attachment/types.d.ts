interface IAttachment {
  id: Id
  project: number
  comment: string
  name: string
  filename: string
  file_extension: string
  size: number
  size_humanize: string
  content_type: number
  object_id: Id
  user: number
  file: string
  url: string
  link: string
}

interface IAttachmentWithUid extends IAttachment {
  uid: string
  status?: UploadFileStatus
}

interface IAttachmentCreate {
  project: number
  comment?: string
  content_type?: string
  object_id?: Id
}
