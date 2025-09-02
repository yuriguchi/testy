interface UserState {
  userModal: User | null
  userConfig: UserConfig
  modal: {
    isShow: boolean
    isEditMode: boolean
  }
  modalProfile: {
    isShow: boolean
  }
}

interface User {
  id: Id
  url: string
  username: string
  first_name: string
  last_name: string
  email: string
  is_active: boolean
  date_joined: string
  groups: number[]
  avatar_link: string
  is_superuser: boolean
}

interface UserWithRoles extends User {
  roles: Role[]
}

interface UserCreate {
  email: string
  password: string
  first_name: string
  last_name: string
}

interface UserUpdate {
  first_name: string
  last_name: string
}

interface UserConfig {
  ui: {
    is_open_sidebar: boolean
    drawer_size_test_case_details: number
    drawer_size_test_result_details: number
    graph_base_type: "pie" | "bar"
    graph_base_bar_type: "by_time" | "by_attr"
    graph_base_bar_attribute_input: string
    test_plan: Record<string, { start_date: string; end_date: string }>
    test_plan_estimate_everywhere_period: EstimatePeriod
  }
  projects?: {
    is_only_favorite: boolean
    is_show_archived: boolean
    favorite: number[]
  }
  test_plans?: {
    is_show_archived: boolean
    shown_columns?: string[]
    is_cases_filter_open: boolean
    filters: Record<string, Record<string, string>>
  }
  test_suites: {
    filters: Record<string, Record<string, string>>
  }
  test_cases?: {
    is_show_archived: boolean
  }
  crop?: string
}

interface GetUsersQuery {
  id?: number
  username?: string
  email?: string
  first_name?: string
  last_name?: string
  is_active?: boolean
  project?: number
  exclude_external?: number
}
