import { createSlice } from "@reduxjs/toolkit"

import { RootState } from "app/store"

const initialState: ProjectState = {
  showArchived: false,
  isOnlyFavorites: false,
}

export const projectSlice = createSlice({
  name: "project",
  initialState,
  reducers: {
    showArchived: (state) => {
      state.showArchived = !state.showArchived
    },
    setIsOnlyFavorites: (state) => {
      state.isOnlyFavorites = !state.isOnlyFavorites
    },
  },
})

export const { showArchived, setIsOnlyFavorites } = projectSlice.actions

export const selectArchivedIsShow = (state: RootState) => state.project.showArchived
export const selectIsOnlyFavorites = (state: RootState) => state.project.isOnlyFavorites

export const projectReducer = projectSlice.reducer
