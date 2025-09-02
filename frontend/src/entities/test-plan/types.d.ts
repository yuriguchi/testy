interface TestPlanState {
  showArchivedResults: boolean
  tests: Test[]
}

interface TestPlansQuery {
  project: number
  is_archive?: boolean
  plan?: number[]
  suite?: number[]
  treesearch?: string
  ordering?: string
  assignee?: string[]
  parent?: number | null
  labels?: number[]
  not_labels?: number[]
  labels_condition?: string
  last_status?: string[]
  test_plan_started_after?: string
  test_plan_started_before?: string
  test_plan_created_after?: string
  test_plan_created_before?: string
  test_created_after?: string
  test_created_before?: string
}

type TestPlansUnionQuery = Omit<TestPlansQuery, "treesearch"> & { search?: string }

interface TestPlanQuery extends TestPlansQuery {
  testPlanId: string
}

interface TestPlan {
  id: Id
  name: string
  title: string
  description: string
  project: number
  parent: Parent | null
  parameters: number[]
  attachments: IAttachment[]
  started_at: string
  due_date: string
  finished_at: string | null
  is_archive: boolean
  url: string
  is_leaf: boolean
  has_children: boolean
  labels?: string[]
  plan_path: string
  attributes: AttributesObject
  started_at: string | null
  created_at: string
}

interface TestPlanUpdate {
  name: string
  description: string
  parent: number | null
  attachments: number[]
  test_cases: string[]
  started_at: string
  due_date: string
  attributes: AttributesObject
}

interface TestPlanCreate extends TestPlan {
  description: string
  test_cases: string[]
  parent: number | null
  started_at: Dayjs
  due_date: Dayjs
  attachments: number[]
  attributes: AttributesObject
}

interface TestPlanStatistics {
  label: string
  value: number
  estimates: number
  empty_estimates: number
  color: string
  id: number
}

interface TestPlanParents {
  id: Id
  title: string
  parent: TestPlanParents | null
}

interface TestPlanStatisticsParams {
  parent: number | null
  project: number
  labels?: number[]
  not_labels?: number[]
  labels_condition?: string
  estimate_period?: EstimatePeriod
  is_archive?: boolean
}

interface TestPlanActivityPagination {
  next: null | number
  previous: null | number
}

interface BreadCrumbsActivityResult {
  id: number
  title: string
  parent: BreadCrumbsActivityResult | null
}

interface TestPlanActivityResult {
  id: number
  action: TestPlanActivityAction
  action_timestamp: string
  breadcrumbs: BreadCrumbsActivityResult
  status_text: string
  status_color: string
  status: number
  test_id: number
  test_name: string
  username: string
  avatar_link: string | null
}

type TestPlanActivityAction = "added" | "deleted" | "updated" | "unknown"

interface TestPlanActivityParams {
  testPlanId: string
  page_size?: number
  page?: number
  search?: string
}

interface TestPlanSuite {
  id: Id
  name: string
  children: TestPlanSuite[]
}

interface TestPlanDescendantsTree {
  id: Id
  title: string
  children: TestPlanDescendantsTree[]
}

interface TestPlanCasesParams {
  testPlanId: string
  include_children?: boolean
}

interface TestPlanHistogramParams {
  project: number
  parent: number | null
  start_date?: string
  end_date?: string
  attribute?: string
  labels?: number[]
  not_labels?: number[]
  labels_condition?: string
  is_archive?: boolean
}

interface TestPlanHistogramDataPoint {
  label: string
  color: string
  count: number
}

type TestPlanHistogramData = {
  point: string
} & Record<number, TestPlanHistogramDataPoint>

interface TestPlanCopyItem {
  plan: number
  new_name?: string
  started_at?: string
  due_date?: string
}

interface TestPlanCopyBody {
  plans: TestPlanCopyItem[]
  dst_plan?: number
  keep_assignee?: boolean
}

interface GetAncestors {
  id: number
  project: number
  _n?: string | number
}

interface GetTestPlanLabelsParams {
  project: number
  parent: number | string | null
}
