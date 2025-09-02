import { useEffect } from "react"

import { useAppDispatch, useAppSelector } from "app/hooks"

import { selectUser } from "entities/auth/model"

import { config } from "shared/config"

import {
  selectNotificationWSMessage,
  websocketConnected,
  websocketDisconnected,
} from "./notification-ws-slice"

export const useNotificationWS = () => {
  const dispatch = useAppDispatch()
  const user = useAppSelector(selectUser)
  const message = useAppSelector(selectNotificationWSMessage)

  useEffect(() => {
    if (!user) {
      dispatch(websocketDisconnected())
      return
    }

    const url = `${config.apiRoot}/ws/notifications/${user.id}/`.replace("http", "ws")
    dispatch(websocketConnected({ url }))

    return () => {
      dispatch(websocketDisconnected())
    }
  }, [dispatch, user])

  const notificationsCount = message?.count ?? 0

  return {
    notificationsCount,
    hasNotifications: notificationsCount > 0,
  }
}
