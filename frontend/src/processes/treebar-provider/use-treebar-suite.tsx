import { useCallback, useContext, useMemo } from "react"
import { useParams, useSearchParams } from "react-router-dom"

import { useLazyGetTestSuiteAncestorsQuery, useLazyGetTestSuitesQuery } from "entities/suite/api"

import { ProjectContext } from "pages/project"

import { config } from "shared/config"
import { LazyNodeProps, NodeId, TreeNodeFetcher } from "shared/libs/tree"

import { TreeSettings } from "widgets/[ui]/treebar/utils"

import { makeNode } from "./utils"

interface Props {
  treeSettings: TreeSettings
  searchDebounce: string
}

export const useTreebarSuite = ({ treeSettings, searchDebounce }: Props) => {
  const { project } = useContext(ProjectContext)!
  const { testSuiteId } = useParams<ParamTestSuiteId>()
  const [searchParams] = useSearchParams()

  const [getSuites] = useLazyGetTestSuitesQuery()
  const [getAncestors] = useLazyGetTestSuiteAncestorsQuery()

  const fetcher: TreeNodeFetcher<Suite, LazyNodeProps> = useCallback(
    async (params, additionalParams) => {
      const res = await getSuites(
        {
          project: project.id,
          page: params.page,
          parent: params.parent ? Number(params.parent) : null,
          page_size: config.defaultTreePageSize,
          ordering: `${treeSettings.suites.sortBy === "desc" ? "-" : ""}${treeSettings.suites.filterBy}`,
          treesearch: searchDebounce,
          _n: params._n,
          ...additionalParams,
        },
        true
      ).unwrap()
      const data = makeNode(res.results, params)
      return { data, nextInfo: res.pages, _n: params._n }
    },
    [treeSettings.suites, searchDebounce]
  )

  const initDependencies = useMemo(() => {
    return [searchParams.get("rootId"), searchDebounce, treeSettings.suites]
  }, [treeSettings.suites, searchDebounce, searchParams.get("rootId")])

  const fetcherAncestors = (id: NodeId) => {
    return getAncestors({ project: project.id, id: Number(id) }).unwrap()
  }

  return {
    fetcher,
    fetcherAncestors,
    initDependencies,
    skipInit: false,
    selectedId: testSuiteId ?? null,
  }
}
