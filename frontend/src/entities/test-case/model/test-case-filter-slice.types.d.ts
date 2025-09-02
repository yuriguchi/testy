interface TestCaseStateFilters {
  filter: TestCaseDataFilters
  settings: FilterSettings
  ordering: string
}

interface TestCaseDataFilters {
  name_or_id: string
  suites: number[]
  is_archive?: boolean
  labels: number[]
  not_labels: number[]
  labels_condition?: LabelCondition
  test_suite_created_before?: string
  test_suite_created_after?: string
  test_case_created_before?: string
  test_case_created_after?: string
  _n?: number
}
