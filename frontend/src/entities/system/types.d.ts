interface SystemState {
  messages: SystemMessage[]
  hiddenMessageIds: number[]
  theme: ThemeType
}

interface SystemMessage {
  id: number
  content: string
  level: number
  is_active: boolean
  is_closing: boolean
  created_at: string
  updated_at: string
}

interface SystemStatistic {
  cases_count: number
  plans_count: number
  projects_count: number
  suites_count: number
  tests_count: number
}

type ThemeType = "dark" | "light"
