interface Result {
  id: Id
  project: number
  status: number
  status_text: string
  status_color: string
  test: number
  user: number
  comment: string
  user_full_name: string
  avatar_link: string | null
  test_case_version?: number
  is_archive: boolean
  created_at: string
  updated_at: string
  url: string
  execution_time: number
  attachments: IAttachment[]
  attributes: AttributesObject
  steps_results: StepResult[]
}

interface ResultQuery {
  testId: string | undefined
  project: string
  showArchive: boolean
}

interface ResultCreate {
  test: number
  status?: number
  comment?: string
  is_archive?: boolean
  execution_time?: number
  attachments?: number[]
  attributes?: AttributesObject
  steps_results?: StepResultCreate[]
}

interface ResultUpdate {
  test: number
  status?: number
  comment?: string
  is_archive?: boolean
  execution_time?: number
  attachments?: number[]
  attributes?: AttributesObject
  steps_results?: StepResultUpdate[]
}

interface StepResult {
  id: number
  step: number
  name: string
  status: number
  status_text: string
  status_color: string
  sort_order: number
}

interface StepResultCreate {
  step: string
  status: number
}

interface ResultFormData {
  comment: string
  status: number | null
  attachments?: number[]
  steps?: Record<string, number>
  attributes?: Attribute[]
}
