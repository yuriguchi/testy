import {
  DependencyList,
  Dispatch,
  PropsWithChildren,
  RefObject,
  SetStateAction,
  createContext,
  useMemo,
  useRef,
  useState,
} from "react"
import { useLocation, useSearchParams } from "react-router-dom"

import { useDebounce } from "shared/hooks"
import { LazyNodeProps, LazyTreeApi, TreeFetcherAncestors, TreeNodeFetcher } from "shared/libs/tree"

import { TreeSettings, getTreeSettingsLS, updateTreeSettingsLS } from "widgets/[ui]/treebar/utils"

import { useTreebarPlan } from "./use-treebar-plan"
import { useTreebarSuite } from "./use-treebar-suite"

interface TreebarProviderContextType {
  treebar:
    | RefObject<LazyTreeApi<Suite, LazyNodeProps>>
    | RefObject<LazyTreeApi<TestPlan, LazyNodeProps>>
  searchText: string
  treeSettings: TreeSettings
  setSearchText: Dispatch<SetStateAction<string>>
  updateTreeSettings: (newSettings: Partial<TreeSettings>) => void
  fetcher: TreeNodeFetcher<TestPlan | Suite, LazyNodeProps>
  fetcherAncestors: TreeFetcherAncestors
  skipInit: boolean
  initParent: string | null
  selectedId: string | null
  initDependencies: DependencyList
  activeTab: "suites" | "plans"
}

export const TreebarContext = createContext<TreebarProviderContextType | null>(null)

export const TreebarProvider = ({ children }: PropsWithChildren) => {
  const [searchParams] = useSearchParams()
  const location = useLocation()

  const treebarSuite = useRef<LazyTreeApi<Suite, LazyNodeProps>>(null)
  const treebarPlan = useRef<LazyTreeApi<TestPlan, LazyNodeProps>>(null)

  const [treeSettings, setTreeSettings] = useState(getTreeSettingsLS())
  const [searchText, setSearchText] = useState(searchParams.get("treeSearch") ?? "")
  const searchDebounce = useDebounce(searchText, 250, true)
  const initParent = searchParams.get("rootId")

  const activeTab = useMemo(() => {
    setSearchText("")
    switch (true) {
      case location.pathname.includes("suites"):
        return "suites"
      case location.pathname.includes("plans"):
        return "plans"
      default:
        return "suites"
    }
  }, [location.pathname])

  const contextSuite = useTreebarSuite({
    treeSettings,
    searchDebounce,
  })
  const contextPlan = useTreebarPlan({
    treeSettings,
    searchDebounce,
  })

  const updateTreeSettings = (newSettings: Partial<TreeSettings>) => {
    setTreeSettings((prevState) => {
      const settings = { ...prevState, ...newSettings }
      updateTreeSettingsLS(settings)
      return settings
    })
  }

  const contextValue: TreebarProviderContextType = useMemo(() => {
    const initDeps =
      activeTab === "suites" ? contextSuite.initDependencies : contextPlan.initDependencies
    const baseValue = {
      treebar: activeTab === "suites" ? treebarSuite : treebarPlan,
      searchText,
      treeSettings,
      initParent,
      updateTreeSettings,
      setSearchText,
      activeTab: activeTab as "suites" | "plans",
    }

    return {
      ...baseValue,
      ...(activeTab === "suites" ? contextSuite : contextPlan),
      initDependencies: [...initDeps, activeTab],
    }
  }, [initParent, activeTab, contextSuite, contextPlan])

  if (!activeTab) {
    return null
  }

  return <TreebarContext.Provider value={contextValue}>{children}</TreebarContext.Provider>
}
