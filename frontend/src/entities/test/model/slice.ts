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
    key: "plan_path",
    title: "Test Plan",
  },
  {
    key: "suite_path",
    title: "Test Suite",
  },
  {
    key: "estimate",
    title: "Estimate",
  },
  {
    key: "labels",
    title: "Labels",
  },
  {
    key: "last_status",
    title: "Last status",
  },
  {
    key: "assignee_username",
    title: "Assignee",
  },
  {
    title: "Created At",
    key: "created_at",
  },
]

const baseTreeColumns = [
  {
    key: "name",
    title: "Name",
  },
  {
    key: "last_status",
    title: "Last status",
  },
  {
    key: "id",
    title: "ID",
  },
  {
    key: "suite_path",
    title: "Test Suite",
  },
  {
    key: "assignee_username",
    title: "Assignee",
  },
  {
    key: "estimate",
    title: "Estimate",
  },
  {
    key: "labels",
    title: "Labels",
  },
  {
    key: "started_at",
    title: "Start Date",
  },
  {
    key: "created_at",
    title: "Created At",
  },
]

const initPagination = queryParamsBySchema(paginationSchema)

const initialState: TestState = {
  test: null,
  settings: {
    table: {
      testPlanId: null,
      columns: baseTableColumns,
      visibleColumns: getVisibleColumns("tests-visible-cols-table") ?? baseTableColumns,
      page: initPagination.page,
      page_size: initPagination.page_size,
      hasBulk: false,
      isAllSelectedTableBulk: false,
      selectedRows: [],
      excludedRows: [],
      _n: 0,
    },
    tree: {
      columns: baseTreeColumns,
      visibleColumns: getVisibleColumns("tests-visible-cols-tree") ?? baseTreeColumns,
    },
  },
}

export const testSlice = createSlice({
  name: "test",
  initialState,
  reducers: {
    setDrawerTest: (state, action: PayloadAction<Test | null>) => {
      state.test = action.payload
    },
    updateSettings: (state, action: PayloadAction<UpdateSettings>) => {
      // @ts-ignore
      state.settings[action.payload.key] = {
        ...state.settings[action.payload.key],
        ...action.payload.settings,
      }
    },
    setSettings: (state, action: PayloadAction<SetSettings>) => {
      // @ts-ignore
      state.settings[action.payload.key] = action.payload
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

export const { setDrawerTest, updateSettings, setSettings, setPagination, clearSettings } =
  testSlice.actions

export const selectDrawerTest = (state: RootState) => state.test.test
export const selectSettings =
  <T>(settingsKey: keyof TestState["settings"]) =>
  (state: RootState): T =>
    state.test.settings[settingsKey] as T

export const testReducer = testSlice.reducer
