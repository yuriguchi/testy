import { PayloadAction, createAction, createSlice } from "@reduxjs/toolkit"

import { RootState } from "app/store"

import { orderingSchema } from "shared/config/query-schemas"
import { formatStringToNumberArray, formatStringToStringArray } from "shared/libs"
import { queryParamsBySchema } from "shared/libs/query-params"

export const testEmptyFilter: TestDataFilters = {
  name_or_id: "",
  plans: [],
  suites: [],
  statuses: [],
  assignee: [],
  labels: [],
  not_labels: [],
  labels_condition: undefined,
  is_archive: undefined,
  test_plan_started_before: undefined,
  test_plan_started_after: undefined,
  test_plan_created_before: undefined,
  test_plan_created_after: undefined,
  test_created_before: undefined,
  test_created_after: undefined,
}

export const testFilterSchema = {
  name_or_id: {
    default: "",
  },
  plans: {
    format: formatStringToNumberArray,
    default: [],
  },
  suites: {
    format: formatStringToNumberArray,
    default: [],
  },
  statuses: {
    format: formatStringToStringArray,
    default: [],
  },
  assignee: {
    format: formatStringToStringArray,
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
  test_plan_started_before: {},
  test_plan_started_after: {},
  test_plan_created_before: {},
  test_plan_created_after: {},
  test_created_before: {},
  test_created_after: {},
}

const initOrdering = queryParamsBySchema(orderingSchema())
const initFilter = queryParamsBySchema(testFilterSchema)

const initialState: TestStateFilters = {
  filter: {
    name_or_id: initFilter.name_or_id,
    plans: initFilter.plans,
    suites: initFilter.suites,
    statuses: initFilter.statuses,
    assignee: initFilter.assignee,
    labels: initFilter.labels,
    not_labels: initFilter.not_labels,
    labels_condition: initFilter.labels_condition,
    is_archive: initFilter.is_archive,
    test_plan_started_before: initFilter.test_plan_started_before,
    test_plan_started_after: initFilter.test_plan_started_after,
    test_plan_created_before: initFilter.test_plan_created_before,
    test_plan_created_after: initFilter.test_plan_created_after,
    test_created_before: initFilter.test_created_before,
    test_created_after: initFilter.test_created_after,
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

export const updateFilter = createAction<Partial<TestStateFilters["filter"]>>(
  "testsFilter/updateFilter"
)

export const testsfilterSlice = createSlice({
  name: "testsFilter",
  initialState,
  reducers: {
    clearFilter: (state) => {
      state.filter = testEmptyFilter
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
    updateOrdering: (state, action: PayloadAction<Partial<TestStateFilters["ordering"]>>) => {
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
  testsfilterSlice.actions

export const selectFilter = (state: RootState) => state.testsFilter.filter
export const selectFilterCount = (state: RootState) => {
  return Object.entries(state.testsFilter.filter).reduce((count, [key, value]) => {
    const defaultValue = testEmptyFilter[key as keyof TestDataFilters]

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
export const selectFilterSettings = (state: RootState) => state.testsFilter.settings
export const selectOrdering = (state: RootState) => state.testsFilter.ordering

export const testsfilterReducer = testsfilterSlice.reducer
