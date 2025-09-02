interface TestCaseState {
  drawerTestCase: TestCase | null
  editingTestCase: TestCase | null
  settings: {
    table: TestCaseTableParams
    tree: TestCaseTreeParams
  }
}

interface TestCaseTableParams {
  page: number
  page_size: number
  visibleColumns: ColumnParam[]
  columns: ColumnParam[]
  sorter?: SorterResult<string>
  _n?: number
}

interface TestCaseTreeParams {
  columns: ColumnParam[]
  visibleColumns: ColumnParam[]
}

interface TestCase {
  id: Id
  name: string
  project: number
  suite_path: string
  suite: { id: number; name: string }
  setup: string
  scenario?: string
  expected: string | null
  steps: Step[]
  is_steps: boolean
  is_leaf: boolean
  has_children: boolean
  teardown: string
  estimate?: string | null
  description: string
  current_version: string
  versions: number[]
  attachments: IAttachment[]
  url: string
  labels: LabelInForm[]
  is_archive: boolean
  source_archived: boolean
  test_suite_description?: string | null
  attributes: AttributesObject
  parent: Parent | null
}

interface TestCaseCreate {
  name: string
  project: number
  suite: number
  scenario?: string
  expected?: string
  steps?: StepUpload[]
  is_steps?: boolean
  setup?: string
  teardown?: string
  estimate?: string
  description?: string
  attachments?: number[]
  attributes?: AttributesObject
}

interface TestCaseUpdate extends TestCase {
  suite: number
  attachments?: number[]
  steps: StepUpload[] | StepAttachNumber[]
  skip_history?: boolean
}

interface Step {
  id: string
  name: string
  scenario: string
  sort_order: number
  attachments: IAttachment[]
  expected?: string
}

interface StepAttachNumber {
  id: string
  name: string
  scenario: string
  scenario: string
  expected: string
  sort_order: number
  attachments: number[]
}

interface StepUpload {
  name: string
  scenario: string
  sort_order: number
  attachments?: number[]
}

interface GetTestCasesQuery {
  testSuiteId: Id
  project: string
  suite?: number[]
  search?: string
  ordering?: string
  page?: number
  page_size?: number
  is_archive?: boolean
  treeview?: boolean
  labels?: number[]
  not_labels?: number[]
  labels_condition?: LabelCondition
  show_descendants?: boolean
  _n?: number
}

type SearchTestCasesQuery = Omit<GetTestCasesQuery, "testSuiteId">

interface TestCaseFormData {
  name: string
  scenario: string
  suite: number
  expected?: string
  setup?: string
  teardown?: string
  estimate?: string | null
  description?: string
  attachments?: number[]
  steps?: Step[]
  is_steps?: boolean
  labels?: LabelInForm[]
  attributes?: Attribute[]
}

interface TestCaseCopyBody {
  cases: TestCaseCopyItem[]
  dst_suite_id: string
}

interface TestCaseCopyItem {
  id: string
  new_name: string
}

interface TestCaseHistoryChange {
  action: "Created" | "Updated" | "Deleted"
  history_date: string
  version: number
  user: User | null
}

interface TestCaseTestsList {
  testCaseId: number
  ordering?: string
  last_status?: string
  is_archive?: boolean
}

interface GetTestCaseByIdParams {
  testCaseId: string
  version?: string
}
