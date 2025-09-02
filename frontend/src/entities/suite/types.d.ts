interface Suite {
  id: Id
  name: string
  description: string
  parent: Parent | null
  project: number
  path: string
  has_children: boolean
  is_leaf: boolean
  cases_count: number
  descendant_count: number
  total_cases_count: number
  estimates: string | null
  total_estimates: string | null
  url: string
  created_at: string
  attachments: IAttachment[]
  attributes: AttributesObject
}

interface SuiteResponseUpdate {
  id: number
  name: string
  description: string
  parent: Parent | null
  project: number
  suite_path: string
  url: string
}

interface SuiteWithCases extends Suite {
  test_cases: TestCase[]
  children: SuiteWithCases[]
}

interface SuiteUpdate {
  name: string
  description: string
  parent: number | null
  attachments: number[]
  attributes: AttributesObject
}

interface SuiteCreate {
  name: string
  project: number
  parent?: number | null
  description?: string
  attributes: AttributesObject
}

interface GetTestSuiteQuery {
  suiteId: string
}

interface GetTestSuitesQuery {
  project: number
  parent?: number | null
  suite?: number[]
  treesearch?: string
  is_archive?: boolean
  ordering?: string
  page?: number
  page_size?: number
  labels?: number[]
  not_labels?: number[]
  labels_condition?: string
  test_case_created_after?: string
  test_case_created_before?: string
  test_suite_created_after?: string
  test_suite_created_before?: string
  _n?: string | number
}

type GetTestSuitesUnionQuery = Omit<GetTestSuitesQuery, "treesearch"> & { search?: string }

interface CopySuiteResponse {
  id: Id
  description: string
  name: string
  parent: Parent | null
  project: number | null
  url: string
  path: string
}

interface SuiteCopyBody {
  suites: SuiteCopyItem[]
  dst_project_id: string
  dst_suite_id?: string
}

interface SuiteCopyItem {
  id: string
  new_name: string
}

interface SuiteDescendantsTree {
  id: number
  name: string
  children: SuiteDescendantsTree[]
}
