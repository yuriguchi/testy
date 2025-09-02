import { PayloadAction, createSlice } from "@reduxjs/toolkit"

import { RootState } from "app/store"

import { paginationSchema } from "shared/config/query-schemas"
import { getVisibleColumns } from "shared/libs"
import { queryParamsBySchema } from "shared/libs/query-params"

import { updateFilter } from "./filter-slice"

const baseTableColumns = [
  {
    key: "id",
    title: "ID",
  },
  {
    key: "name",
    title: "Name",
  },
  {
    key: "suite_path",
    title: "Test Suite",
  },
  {
    key: "labels",
    title: "Labels",
  },
  {
    key: "estimate",
    title: "Estimate",
  },
  {
    key: "created_at",
    title: "Created At",
  },
]

const baseTreeColumns = [
  {
    key: "name",
    title: "Name",
  },
  {
    key: "id",
    title: "ID",
  },
  {
    key: "labels",
    title: "Labels",
  },
  {
    key: "estimate",
    title: "Estimate",
  },
  {
    key: "created_at",
    title: "Created At",
  },
]

const initPagination = queryParamsBySchema(paginationSchema)

const initialState: TestCaseState = {
  drawerTestCase: null,
  editingTestCase: null,
  settings: {
    table: {
      columns: baseTableColumns,
      visibleColumns: getVisibleColumns("test-cases-visible-cols-table") ?? baseTableColumns,
      page: initPagination.page,
      page_size: initPagination.page_size,
      _n: 0,
    },
    tree: {
      columns: baseTreeColumns,
      visibleColumns: getVisibleColumns("test-cases-visible-cols-tree") ?? baseTreeColumns,
    },
  },
}

export const testCaseSlice = createSlice({
  name: "testCase",
  initialState,
  reducers: {
    setDrawerTestCase: (state, action: PayloadAction<TestCase | null>) => {
      state.drawerTestCase = action.payload
    },
    setDrawerTestCaseIsArchive: (state, action: PayloadAction<boolean>) => {
      if (state.drawerTestCase) {
        state.drawerTestCase = { ...state.drawerTestCase, is_archive: action.payload }
      }
    },
    clearDrawerTestCase: (state) => {
      state.drawerTestCase = null
    },
    updateSettings: (state, action: PayloadAction<UpdateSettings>) => {
      // @ts-ignore
      state.settings[action.payload.key] = {
        ...state.settings[action.payload.key],
        ...action.payload.settings,
      }
    },
    setPagination: (state, action: PayloadAction<SetPagination>) => {
      // @ts-ignore
      state.settings[action.payload.key] = {
        ...state.settings[action.payload.key],
        page: action.payload.pagination.page,
        page_size: action.payload.pagination.page_size,
      }
    },
    clearSettings: (state) => {
      state.settings = {
        tree: initialState.settings.tree,
        table: {
          ...initialState.settings.table,
          page: 1,
          page_size: 10,
        },
      }
    },
  },
  extraReducers: (builder) => {
    builder.addCase(updateFilter, (state) => {
      state.settings.table.page = 1
      state.settings.table.page_size = initialState.settings.table.page_size
    })
  },
})

export const {
  setDrawerTestCase,
  clearDrawerTestCase,
  setDrawerTestCaseIsArchive,
  updateSettings,
  clearSettings,
  setPagination,
} = testCaseSlice.actions

export const testCaseReducer = testCaseSlice.reducer

export const selectSettings =
  <T>(settingsKey: keyof TestState["settings"]) =>
  (state: RootState): T =>
    state.testCase.settings[settingsKey] as T
export const selectDrawerTestCase = (state: RootState) => state.testCase.drawerTestCase
