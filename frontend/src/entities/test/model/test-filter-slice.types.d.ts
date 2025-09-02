interface TestStateFilters {
  filter: TestDataFilters
  settings: FilterSettings
  ordering: string
}

interface TestDataFilters {
  name_or_id: string
  plans: number[]
  suites: number[]
  statuses: string[]
  assignee: string[]
  labels: number[]
  not_labels: number[]
  labels_condition?: LabelCondition
  is_archive?: boolean
  test_plan_started_before?: string
  test_plan_started_after?: string
  test_plan_created_before?: string
  test_plan_created_after?: string
  test_created_before?: string
  test_created_after?: string
  _n?: number
}

interface FilterSettings {
  selected: string | null
  editing: boolean
  editingValue: string
  creatingNew: boolean
  hasUnsavedChanges: boolean
}
