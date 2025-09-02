import { Alert } from "antd"
import { useMemo } from "react"

import { useAppDispatch, useAppSelector } from "app/hooks"

import { useGetSystemMessagesQuery } from "entities/system/api"
import { addHiddenMessageId, selectHiddenMessages } from "entities/system/model/slice"

import "./styles.css"

const formatType: Record<number, "info" | "warning" | "error"> = {
  0: "info",
  1: "warning",
  2: "error",
}

export const SystemMessages = () => {
  const dispatch = useAppDispatch()
  const hiddenMessages = useAppSelector(selectHiddenMessages)
  const { data: messages, isLoading } = useGetSystemMessagesQuery()

  const handleMessageClose = (id: number) => {
    dispatch(addHiddenMessageId(id))
  }

  const messagesClear = useMemo(() => {
    if (!messages) return []
    if (!hiddenMessages.length) return messages
    return messages.filter((item) => !hiddenMessages.includes(item.id))
  }, [messages])

  if (isLoading || !messages?.length) return null

  return (
    <div className="wrapper-system-messages">
      {messagesClear.map((item) => (
        <div key={item.id} className="system-message">
          <Alert
            message={item.content}
            type={formatType[item.level]}
            showIcon
            closable={item.is_closing}
            className={`system-alert-type-${formatType[item.level]}`}
            onClose={() => handleMessageClose(item.id)}
          />
        </div>
      ))}
    </div>
  )
}
