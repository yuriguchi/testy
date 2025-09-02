import { AnyAction, Middleware } from "@reduxjs/toolkit"

import {
  websocketConnected,
  websocketDisconnected,
  websocketMessageReceived,
} from "../model/notification-ws-slice"

export const notificationWSMiddleware: Middleware = (storeAPI) => {
  let socket: WebSocket | null = null
  let isConnected = false

  return (next) => (action: AnyAction) => {
    if (websocketConnected.match(action)) {
      if (!socket) {
        socket = new WebSocket(action.payload.url)
      }

      socket.onopen = () => {
        // eslint-disable-next-line no-console
        console.log("Notification WebSocket connected")
        isConnected = true
      }

      socket.onmessage = (event: { data: string }) => {
        const message = JSON.parse(event.data) as NotificationWSMessage
        storeAPI.dispatch(websocketMessageReceived(message))
      }

      socket.onclose = () => {
        storeAPI.dispatch(websocketDisconnected())
      }

      socket.onerror = (error) => {
        console.error("Notification WebSocket error", error)
      }
    } else if (websocketDisconnected.match(action)) {
      if (socket && isConnected) {
        socket.close()
        isConnected = false
        // eslint-disable-next-line no-console
        console.log("Notification WebSocket disconnected")
      }
      socket = null
    }

    return next(action)
  }
}
