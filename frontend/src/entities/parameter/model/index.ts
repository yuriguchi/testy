import { PayloadAction, createSlice } from "@reduxjs/toolkit"

import { RootState } from "app/store"

const initialState: ParameterState = {
  parameter: null,
  modal: {
    isShow: false,
    isEditMode: false,
  },
}

export const parameterSlice = createSlice({
  name: "parameter",
  initialState,
  reducers: {
    setParameter: (state, action: PayloadAction<IParameter>) => {
      state.parameter = action.payload
    },
    showCreateParameterModal: (state) => {
      state.modal.isShow = true
    },
    showEditParameterModal: (state) => {
      state.modal.isShow = true
      state.modal.isEditMode = true
    },
    hideModal: (state) => {
      state.modal.isShow = false
      state.modal.isEditMode = false
    },
  },
})

export const { setParameter, showCreateParameterModal, showEditParameterModal, hideModal } =
  parameterSlice.actions

export const selectModalIsShow = (state: RootState) => state.parameter.modal.isShow
export const selectModalIsEditMode = (state: RootState) => state.parameter.modal.isEditMode
export const selectParameter = (state: RootState) => state.parameter.parameter

export default parameterSlice.reducer
