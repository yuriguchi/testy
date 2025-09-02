import { useCallback, useContext, useMemo } from "react"
import { useParams, useSearchParams } from "react-router-dom"

import { useLazyGetTestPlanAncestorsQuery, useLazyGetTestPlansQuery } from "entities/test-plan/api"

import { ProjectContext } from "pages/project"

import { config } from "shared/config"
import { LazyNodeProps, NodeId, TreeNodeFetcher } from "shared/libs/tree"

import { TreeSettings } from "widgets/[ui]/treebar/utils"

import { makeNode } from "./utils"

interface Props {
  treeSettings: TreeSettings
  searchDebounce: string
}

export const useTreebarPlan = ({ treeSettings, searchDebounce }: Props) => {
  const { project } = useContext(ProjectContext)!
  const { testPlanId } = useParams<ParamTestPlanId>()
  const [searchParams] = useSearchParams()

  const [getPlans] = useLazyGetTestPlansQuery()
  const [getAncestors] = useLazyGetTestPlanAncestorsQuery()

  const fetcher: TreeNodeFetcher<TestPlan, LazyNodeProps> = useCallback(
    async (params, additionalParams) => {
      const res = await getPlans(
        {
          project: project.id,
          page: params.page,
          parent: params.parent ? Number(params.parent) : null,
          page_size: config.defaultTreePageSize,
          ordering: `${treeSettings.plans.sortBy === "desc" ? "-" : ""}${treeSettings.plans.filterBy}`,
          treesearch: searchDebounce,
          is_archive: treeSettings.show_archived,
          _n: params._n,
          ...additionalParams,
        },
        true
      ).unwrap()
      const data = makeNode(res.results, params)
      return { data, nextInfo: res.pages, _n: params._n }
    },
    [treeSettings.plans, treeSettings.show_archived, searchDebounce]
  )

  const initDependencies = useMemo(() => {
    return [
      searchParams.get("rootId"),
      searchDebounce,
      treeSettings.show_archived,
      treeSettings.plans,
    ]
  }, [treeSettings.show_archived, treeSettings.plans, searchDebounce, searchParams.get("rootId")])

  const fetcherAncestors = (id: NodeId) => {
    return getAncestors({ project: project.id, id: Number(id) }).unwrap()
  }

  return {
    fetcher,
    fetcherAncestors,
    initDependencies,
    skipInit: false,
    selectedId: testPlanId ?? null,
  }
}
