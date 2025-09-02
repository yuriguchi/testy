interface CommentType {
  id: number
  content: string
  user: User
  attachments: IAttachment[]
  created_at: string
  updated_at: string
  deleted_at: string | null
}

interface GetCommentsRequest {
  comment_id?: string
  model: Models
  object_id: string
  ordering?: string
}

interface AddCommentsRequest {
  model: Models
  object_id: string
  content: string
  attachments?: string[]
}

interface UpdateCommentsRequest {
  comment_id: number
  content: string
  attachments?: string[]
}
