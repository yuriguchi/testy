import { PayloadAction, createSlice } from "@reduxjs/toolkit"

import { RootState } from "app/store"

const initialState: TestPlanState = {
  showArchivedResults: false,
  tests: [],
}

export const testPlanSlice = createSlice({
  name: "testPlan",
  initialState,
  reducers: {
    showArchivedResults: (state) => {
      state.showArchivedResults = !state.showArchivedResults
    },
    setTests: (state, action: PayloadAction<Test[]>) => {
      state.tests = action.payload
    },
  },
})

export const { showArchivedResults, setTests } = testPlanSlice.actions

export const testPlanReducer = testPlanSlice.reducer

export const selectArchivedResultsIsShow = (state: RootState) => state.testPlan.showArchivedResults
export const selectTests = (state: RootState) => state.testPlan.tests
