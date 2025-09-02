import { PayloadAction, createSlice } from "@reduxjs/toolkit"

import { RootState } from "app/store"

const initialState: AppState = {
  error: null,
}

export const appSlice = createSlice({
  name: "app",
  initialState,
  reducers: {
    handleError: (state, action: PayloadAction<ErrorState | null>) => {
      state.error = action.payload
    },
  },
})

export const { handleError } = appSlice.actions

export const appReducer = appSlice.reducer
export const selectAppError = (state: RootState) => state.app.error
