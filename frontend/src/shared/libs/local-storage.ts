export const savePrevPageUrl = (url: string) => {
  localStorage.setItem("prevPageUrl", url)
}

export const getPrevPageUrl = () => {
  return localStorage.getItem("prevPageUrl")
}

export const clearPrevPageUrl = () => {
  localStorage.removeItem("prevPageUrl")
}

export const getLang = () => {
  return localStorage.getItem("lang") ?? "en"
}

export const saveVisibleColumns = (key: string, columns: ColumnParam[]) => {
  localStorage.setItem(key, JSON.stringify(columns))
}

export const getVisibleColumns = (key: string): ColumnParam[] | undefined => {
  const value = localStorage.getItem(key)
  return value ? (JSON.parse(value) as ColumnParam[]) : undefined
}

export const clearVisibleColumns = (key: string) => {
  localStorage.removeItem(key)
}

export const saveSelectedFilter = ({
  name,
  projectId,
  type,
}: {
  name: string
  projectId: number
  type: "plans" | "suites"
}) => {
  localStorage.setItem(`selected-filter-${projectId}-${type}`, name)
}
