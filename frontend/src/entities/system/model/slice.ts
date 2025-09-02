import { PayloadAction, createSlice } from "@reduxjs/toolkit"

import { RootState } from "app/store"

const initialState: SystemState = {
  messages: [],
  hiddenMessageIds: [],
  theme: "light",
}

export const systemSlice = createSlice({
  name: "system",
  initialState,
  reducers: {
    setMessages: (state, action: PayloadAction<SystemMessage[]>) => {
      state.messages = action.payload
    },
    addHiddenMessageId: (state, action: PayloadAction<number>) => {
      state.hiddenMessageIds = (state.hiddenMessageIds ?? []).concat(action.payload)
    },
    setTheme: (state, action: PayloadAction<ThemeType>) => {
      state.theme = action.payload
      localStorage.setItem("theme", action.payload)
    },
  },
})

export const { setMessages, addHiddenMessageId, setTheme } = systemSlice.actions

export const selectSystemMessages = (state: RootState) => state.system.messages
export const selectHiddenMessages = (state: RootState) => state.system.hiddenMessageIds
export const selectTheme = (state: RootState) => {
  const localStorageTheme = localStorage.getItem("theme")
  return localStorageTheme ?? state.system.theme
}

export const systemReducer = systemSlice.reducer
