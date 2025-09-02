type Modify<T, R> = Omit<T, keyof R> & R

type Id = number
type BaseParams = Record<string, string | undefined>
interface ParamTestSuiteId extends BaseParams {
  testSuiteId: string
}
interface ParamProjectId extends BaseParams {
  projectId: string
}
interface ParamTestPlanId extends BaseParams {
  testPlanId: string
}

type AttributeType = "Text" | "List" | "JSON"

interface Attribute {
  id: string
  name: string
  value: string | object
  type: AttributeType
  required?: boolean
  status_specific?: number[]
  is_init: boolean
}

type AttributesObject = Record<string, string[] | string | object>

interface TreeCheckboxInfo {
  checked: boolean
  node: InfoNode
}

type CheckboxChecked =
  | Key[]
  | {
      checked: Key[]
      halfChecked: Key[]
    }

interface InfoNode {
  key: string
  halfChecked: boolean
  test_cases: { id: number; name: string }[]
  children: InfoNode[] | { key: string; title: string }[]
}

interface PaginationResponse<T> {
  count: number
  links: PaginationResponseLinks
  pages: PaginationResponsePages
  results: T
}

interface PaginationResponseLinks {
  next: null | number
  previous: null | number
}

interface PaginationResponsePages {
  current: number
  total: number
  next: null | number
  previous: null | number
}

interface PaginationParams {
  page: number
  page_size: number
}

interface PaginationQuery {
  page_size?: number
  page?: number
  _n?: string | number
}

type QueryWithPagination<T> = PaginationQuery & T

type ModalMode = "edit" | "create"
interface CropPositions {
  left: number
  right: number
  upper: number
  lower: number
}
type Models = "test" | "testcase" | "testresult" | "testsuite" | "testplan"
type Ordering = "asc" | "desc"
type EstimatePeriod = "minutes" | "hours" | "days"
interface BaseData {
  id: Id
  name: string
  title: string
  children?: T[]
}
interface SelectData {
  label: React.ReactNode | string
  value: number
}
// eslint-disable-next-line @typescript-eslint/no-redundant-type-constituents
type DataWithKey<T> = T & BaseData & { key: Key }
interface BaseResponse {
  id: string | Id
  name: string
}
interface Breadcrumbs {
  id: number
  title: string
  parent: Breadcrumbs | null
}
interface Parent {
  id: number
  name: string
}

interface WebSocketState<T> {
  connected: boolean
  messages: T[]
  lastMessage: T | null
}

interface AppState {
  error: ErrorState | null
}

interface ErrorState {
  code: number
  message: string
}

interface ColumnParam {
  key: string
  title: string
}

interface BaseEntity {
  id: number
  parent: Parent | null
}

type HTMLDataAttribute = Record<`data-${string}`, unknown>
