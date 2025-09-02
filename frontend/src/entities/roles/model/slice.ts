import { PayloadAction, createSlice } from "@reduxjs/toolkit"

import { RootState } from "app/store"

const initialState: RoleState = {
  isModalOpen: false,
  mode: "create",
  user: null,
  onSuccess: null,
}

export const rolesSlice = createSlice({
  name: "role",
  initialState,
  reducers: {
    openModal: (
      state,
      action: PayloadAction<{ mode: "create" | "edit"; user?: UserWithRoles }>
    ) => {
      state.isModalOpen = true
      state.mode = action.payload.mode
      state.user = action.payload.user ?? null
      if (action.payload.mode === "edit" && !action.payload.user) {
        console.warn("User is not provided for edit mode")
      }
    },
    closeModal: (state) => {
      state.isModalOpen = false
    },
    setOnSuccess: (state, action: PayloadAction<() => Promise<void>>) => {
      state.onSuccess = action.payload
    },
    resetOnSuccess: (state) => {
      state.onSuccess = null
    },
  },
})

export const {
  openModal: openRoleModal,
  closeModal: closeRoleModal,
  setOnSuccess,
  resetOnSuccess,
} = rolesSlice.actions

export const roleReducer = rolesSlice.reducer

export const selectIsRoleModalOpen = (state: RootState) => state.role.isModalOpen
export const selectRoleModalMode = (state: RootState) => state.role.mode
export const selectRoleUser = (state: RootState) => state.role.user
export const selectRoleOnSuccess = (state: RootState) => state.role.onSuccess
