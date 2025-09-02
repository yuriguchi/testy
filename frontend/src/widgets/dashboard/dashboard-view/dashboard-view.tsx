import { MeContext } from "processes"
import { useContext, useState } from "react"

import { useCacheState, useDebounce } from "shared/hooks"

import { ProjectsDashboardCards, ProjectsDashboardTable } from "widgets/project/ui"

import { DashboardHeader } from "../dashboard-header/dashboard-header"

type ProjectViewType = "table" | "cards"

export const DashboardView = () => {
  const { userConfig, updateConfig } = useContext(MeContext)
  const [searchByNameValue, setSearchByNameValue] = useState<string | undefined>(undefined)
  const searchByNameDebounce = useDebounce(searchByNameValue, 250, true)
  const [view, setView] = useCacheState<ProjectViewType>("dashboard-view", "cards")

  const onShowArchived = async () => {
    await updateConfig({
      ...userConfig,
      projects: {
        ...userConfig?.projects,
        is_show_archived: !userConfig?.projects?.is_show_archived,
      },
    })
  }

  const onIsOnlyFavoriteClick = async () => {
    await updateConfig({
      ...userConfig,
      projects: {
        ...userConfig?.projects,
        is_only_favorite: !userConfig?.projects?.is_only_favorite,
      },
    })
  }

  return (
    <>
      <DashboardHeader
        onChangeSearch={(value) => setSearchByNameValue(value)}
        searchText={searchByNameValue ?? ""}
        onShowArchived={onShowArchived}
        onIsOnlyFavoriteClick={onIsOnlyFavoriteClick}
        view={view}
        setView={setView}
      />
      {view === "cards" && <ProjectsDashboardCards searchName={searchByNameDebounce ?? ""} />}
      {view === "table" && <ProjectsDashboardTable searchName={searchByNameDebounce ?? ""} />}
    </>
  )
}
