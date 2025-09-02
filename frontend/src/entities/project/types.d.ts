interface ProjectState {
  showArchived: boolean
  isOnlyFavorites: boolean
}

interface ProjectSettings {
  is_result_editable?: boolean
  result_edit_limit?: string | null
  status_order?: Record<string, number>
  default_status?: number | null
}

interface Project {
  id: Id
  url: string
  name: string
  icon?: string | null
  description: string
  is_archive: boolean
  cases_count: number
  suites_count: number
  plans_count: number
  tests_count: number
  is_private: boolean
  is_manageable: boolean
  is_member: boolean
  settings: ProjectSettings
  is_visible: boolean
}

interface ProjectUpdate {
  name: string
  description: string
  is_archive: boolean
  icon?: RcFile
  is_private?: boolean
}

interface ProjectsProgress {
  id: number
  tests_progress_period: number
  tests_progress_total: number
  tests_total: number
  title: string
}

interface ProjectProgressParams {
  period_date_start: string
  period_date_end: string
  projectId: string
}

interface DeletePreviewResponse {
  verbose_name: string
  verbose_name_related_model: string
  count: number
}

interface GetProjectsQuery {
  favorites?: boolean
  is_archive?: boolean
  name?: string
  ordering?: string
}

interface EntityBreadcrumbs {
  id: number
  parent: EntityBreadcrumbs | null
  title: string
}
