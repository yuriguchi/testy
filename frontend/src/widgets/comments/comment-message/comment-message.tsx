import classNames from "classnames"
import { CommentUserInfo } from "entities/comments/ui"
import { useEffect } from "react"
import { useLocation } from "react-router-dom"

import { DeleteComment, EditComment } from "features/comments"

import { AttachmentField, Markdown } from "shared/ui"

import styles from "./styles.module.css"

interface Props {
  comment: CommentType
  isVisibleActions: boolean
}

export const CommentMessage = ({ comment, isVisibleActions }: Props) => {
  const location = useLocation()

  useEffect(() => {
    if (location.hash && location.hash.includes("comment")) {
      const element = document.getElementById(location.hash.substring(1))
      element?.scrollIntoView({ behavior: "smooth" })
    }
  }, [location])

  return (
    <li
      id={`comment-${comment.id}`}
      className={classNames(styles.wrapper, {
        [styles.hashActive]: location.hash === `#comment-${comment.id}`,
      })}
    >
      <CommentUserInfo
        commentId={comment.id}
        username={comment.user.username}
        avatarLink={comment.user.avatar_link}
        createdAt={comment.created_at}
        updatedAt={comment.updated_at}
      />
      {comment.deleted_at === null ? (
        <div data-testid={`comment-${comment.id}-content`}>
          <Markdown content={comment.content} />
        </div>
      ) : (
        <span style={{ fontStyle: "italic" }} data-testid={`comment-${comment.id}-content-deleted`}>
          {comment.content}
        </span>
      )}
      <AttachmentField attachments={comment.attachments} isDivider={false} />
      {isVisibleActions && (
        <div className={styles.actions}>
          <EditComment comment={comment} />
          <DeleteComment commentId={comment.id} />
        </div>
      )}
    </li>
  )
}
