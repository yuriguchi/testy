interface TestState {
  test: Test | null
  settings: {
    table: TestTableParams
    tree: TestTreeParams
  }
}

type TestStateSettings = TestState["settings"][keyof TestState["settings"]]

interface SetSettings {
  key: keyof TestState["settings"]
  settings: TestStateSettings
}

interface UpdateSettings extends SetSettings {
  settings: Partial<TestStateSettings>
}

interface SetPagination {
  key: keyof TestState["settings"]
  pagination: PaginationParams
}

interface Test {
  id: Id
  project: number
  has_children: boolean
  is_leaf: boolean
  case: number
  name: string
  title: string
  last_status: number
  last_status_color: string
  last_status_name: string
  plan: number
  suite: number
  user: number
  is_archive: boolean
  created_at: string
  updated_at: string
  url: string
  suite_path: string
  plan_path: string
  assignee: string | null
  assignee_username: string | null
  avatar_link: string | null
  test_suite_description?: string | null
  estimate: string | null
  labels: Pick<Label, "id" | "name">[]
  parent?: Parent | null
}

interface TestGet {
  testPlanId?: Id
  project: number
  is_archive: boolean
}

interface TestGetFilters extends TestGet {
  last_status?: string[]
  search?: string
  ordering?: string
  labels?: number[]
  not_labels?: number[]
  labels_condition?: string
  is_archive?: boolean
  suite?: number[]
  plan?: number[]
  nested_search?: boolean
  assignee?: string[]
  unassigned?: boolean
  show_descendants?: boolean
  test_plan_started_before?: string
  test_plan_started_after?: string
  test_plan_created_before?: string
  test_plan_created_after?: string
  test_created_before?: string
  test_created_after?: string
  _n?: string | number
}

interface TestTableParams {
  page: number
  page_size: number
  testPlanId: number | null
  visibleColumns: ColumnParam[]
  columns: ColumnParam[]
  sorter?: SorterResult<string>
  hasBulk: boolean
  isAllSelectedTableBulk: boolean
  selectedRows: number[]
  excludedRows: number[]
  _n?: number
}

interface TestTreeParams {
  columns: ColumnParam[]
  visibleColumns: ColumnParam[]
}

interface TestTableFilters {
  plan?: number
  project?: string
  is_archive?: boolean[]
  page_size?: number
  page?: number
  last_status?: string[]
  name?: FilterValue
  labels?: string[]
  not_labels?: string[]
  labels_condition?: string
  ordering?: string
  suite?: string[]
  assignee_id?: string
  unassigned?: boolean
  suite_path?: FilterValue
}

interface TestUpdate {
  case?: number
  plan?: number
  assignee?: string
  is_archive?: boolean
}

interface TestBulkUpdate {
  included_tests: number[]
  excluded_tests: number[]
  current_plan: number
  plan?: number
  assignee?: string
  filter_conditions?: Partial<TestGetFilters>
}

interface TestsWithPlanBreadcrumbs extends Test {
  breadcrumbs: BreadCrumbsActivityResult
}
