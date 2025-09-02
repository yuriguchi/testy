import { RootState } from "app/store"
import { createWebsocketSlice, getInitialState } from "app/websocket-slice"

const notificationWSSlice = createWebsocketSlice<NotificationWSMessage>(
  "notificationWS",
  getInitialState<NotificationWSMessage>()
)

export const { websocketConnected, websocketDisconnected, websocketMessageReceived } =
  notificationWSSlice.actions

export const notificationWSReducer = notificationWSSlice.reducer

export const selectNotificationWSConnected = (state: RootState) => state.notificationWS.connected
export const selectNotificationWSMessages = (state: RootState) => state.notificationWS.messages
export const selectNotificationWSMessage = (state: RootState) => state.notificationWS.lastMessage
