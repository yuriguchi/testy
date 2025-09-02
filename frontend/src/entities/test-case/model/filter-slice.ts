import { PayloadAction, createAction, createSlice } from "@reduxjs/toolkit"

import { RootState } from "app/store"

import { formatStringToNumberArray } from "shared/libs"
import { queryParamsBySchema } from "shared/libs/query-params"

export const testCasesOrderingSchema = {
  ordering: {
    default: "name",
  },
}

export const testCasesEmptyFilter: TestCaseDataFilters = {
  name_or_id: "",
  suites: [],
  is_archive: undefined,
  labels: [],
  not_labels: [],
  labels_condition: undefined,
  test_suite_created_before: undefined,
  test_suite_created_after: undefined,
  test_case_created_before: undefined,
  test_case_created_after: undefined,
}

export const testCasesFilterSchema = {
  name_or_id: {
    default: "",
  },
  suites: {
    format: formatStringToNumberArray,
    default: [],
  },
  labels: {
    format: formatStringToNumberArray,
    default: [],
  },
  not_labels: {
    format: formatStringToNumberArray,
    default: [],
  },
  labels_condition: {
    format: (value: string) => (value === "and" ? "and" : "or"),
  },
  is_archive: {
    format: (value: string) => value === "true",
  },
  test_suite_created_before: {},
  test_suite_created_after: {},
  test_case_created_before: {},
  test_case_created_after: {},
}

const initOrdering = queryParamsBySchema(testCasesOrderingSchema)
const initFilter = queryParamsBySchema(testCasesFilterSchema)

const initialState: TestCaseStateFilters = {
  filter: {
    name_or_id: initFilter.name_or_id,
    suites: initFilter.suites,
    is_archive: initFilter.is_archive,
    labels: initFilter.labels,
    not_labels: initFilter.not_labels,
    labels_condition: initFilter.labels_condition,
    test_suite_created_before: initFilter.test_suite_created_before,
    test_suite_created_after: initFilter.test_suite_created_after,
    test_case_created_before: initFilter.test_case_created_before,
    test_case_created_after: initFilter.test_case_created_after,
  },
  settings: {
    selected: null,
    editing: false,
    editingValue: "",
    creatingNew: false,
    hasUnsavedChanges: false,
  },
  ordering: initOrdering.ordering,
}

export const updateFilter = createAction<Partial<TestCaseStateFilters["filter"]>>(
  "testCasesFilter/updateFilter"
)

export const testCasesfilterSlice = createSlice({
  name: "testCasesFilter",
  initialState,
  reducers: {
    clearFilter: (state) => {
      state.filter = testCasesEmptyFilter
    },
    updateFilterSettings: (state, action: PayloadAction<Partial<FilterSettings>>) => {
      state.settings = {
        ...state.settings,
        ...action.payload,
      }
    },
    resetFilterSettings: (state) => {
      state.settings = initialState.settings
    },
    updateOrdering: (state, action: PayloadAction<Partial<TestCaseStateFilters["ordering"]>>) => {
      state.ordering = action.payload
    },
  },
  extraReducers: (builder) => {
    builder.addCase(updateFilter, (state, action) => {
      state.filter = {
        ...state.filter,
        ...action.payload,
      }
    })
  },
})

export const { clearFilter, updateFilterSettings, updateOrdering, resetFilterSettings } =
  testCasesfilterSlice.actions

export const selectFilter = (state: RootState) => state.testCasesFilter.filter
export const selectFilterSettings = (state: RootState) => state.testCasesFilter.settings
export const selectFilterCount = (state: RootState) => {
  return Object.entries(state.testCasesFilter.filter).reduce((count, [key, value]) => {
    const defaultValue = testCasesEmptyFilter[key as keyof TestCaseDataFilters]

    if (Array.isArray(value)) {
      if (value.length > 0) {
        return count + 1
      }
    } else if (value !== defaultValue) {
      return count + 1
    }

    return count
  }, 0)
}
export const selectOrdering = (state: RootState) => state.testCasesFilter.ordering

export const testCasesfilterReducer = testCasesfilterSlice.reducer
