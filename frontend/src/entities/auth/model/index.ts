import { PayloadAction, createSlice } from "@reduxjs/toolkit"

import { RootState } from "app/store"

const initialState: AuthState = {
  user: null,
}

const removeCsrfCookie = () => {
  document.cookie = "csrftoken=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT"
}

export const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload
    },
    logout: () => {
      removeCsrfCookie()
      return initialState
    },
  },
})

export const { setUser, logout } = authSlice.actions

export default authSlice.reducer

export const selectUser = (state: RootState) => state.auth.user
