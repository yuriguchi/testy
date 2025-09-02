import { useAppSelector } from "app/hooks"

import { selectUser } from "entities/auth/model"

import { CommentMessage } from "."

interface Props {
  comments: CommentType[]
}

export const CommentList = ({ comments }: Props) => {
  const user = useAppSelector(selectUser)

  return (
    <ul style={{ paddingLeft: 8 }} data-testid="comment-list">
      {comments.map((comment) => {
        const isVisibleActions =
          Number(comment.user.id) === Number(user?.id) && comment.deleted_at === null
        return (
          <CommentMessage key={comment.id} comment={comment} isVisibleActions={isVisibleActions} />
        )
      })}
    </ul>
  )
}
