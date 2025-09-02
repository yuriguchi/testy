import { PayloadAction, createSlice } from "@reduxjs/toolkit"
import { Draft } from "immer"

export interface WebSocketState<T> {
  connected: boolean
  messages: T[]
  lastMessage: T | null
}

export const getInitialState = <T>(): WebSocketState<T> => {
  return {
    connected: false,
    messages: [],
    lastMessage: null,
  }
}

export const createWebsocketSlice = <T>(name: string, initialState: WebSocketState<T>) => {
  return createSlice({
    name,
    initialState,
    reducers: {
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      websocketConnected(state, action: PayloadAction<{ url: string }>) {
        state.connected = true
      },
      websocketDisconnected(state) {
        state.connected = false
        state.lastMessage = null
        state.messages = []
      },
      websocketMessageReceived(state, action: PayloadAction<T>) {
        state.messages = [...state.messages, action.payload as Draft<T>]
        state.lastMessage = action.payload as Draft<T>
      },
    },
  })
}
