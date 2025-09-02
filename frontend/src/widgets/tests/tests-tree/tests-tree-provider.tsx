import { makeNode } from "processes/treebar-provider/utils"
import {
  PropsWithChildren,
  RefObject,
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
} from "react"

import { useAppSelector } from "app/hooks"

import { selectDrawerTest, selectFilter, selectOrdering } from "entities/test/model"

import {
  useLazyGetTestPlanAncestorsQuery,
  useLazyGetTestPlansWithTestsQuery,
} from "entities/test-plan/api"

import { ProjectContext } from "pages/project"

import { config } from "shared/config"
import {
  LazyNodeProps,
  LazyTreeApi,
  NodeId,
  TreeFetcherAncestors,
  TreeNodeFetcher,
} from "shared/libs/tree"

const checkIsOpen = (item: Test | TestPlan, drawerTest: Test | null) => {
  if (item.is_leaf || !drawerTest) {
    return false
  }

  return item.id === Number(drawerTest?.plan)
}

export interface TestsTreeContextType {
  testsTree: RefObject<LazyTreeApi<Test | TestPlan, LazyNodeProps>>
  fetcher: TreeNodeFetcher<Test | TestPlan, LazyNodeProps>
  fetcherAncestors: TreeFetcherAncestors
  skipInit: boolean
}

export const TestsTreeContext = createContext<TestsTreeContextType | null>(null)

export const TestsTreeProvider = ({ children }: PropsWithChildren) => {
  const { project } = useContext(ProjectContext)!

  const testsTree = useRef<LazyTreeApi<Test | TestPlan, LazyNodeProps>>(null)
  const testsFilter = useAppSelector(selectFilter)
  const testsOrdering = useAppSelector(selectOrdering)
  const drawerTest = useAppSelector(selectDrawerTest)

  const [getPlansWithTests] = useLazyGetTestPlansWithTestsQuery()
  const [getAncestors] = useLazyGetTestPlanAncestorsQuery()

  const fetcher: TreeNodeFetcher<Test | TestPlan, LazyNodeProps> = useCallback(
    async (params) => {
      const res = await getPlansWithTests(
        {
          project: project.id,
          page: params.page,
          parent: params.parent ? Number(params.parent) : null,
          page_size: config.defaultTreePageSize,
          ordering: testsOrdering,
          is_archive: testsFilter.is_archive,
          labels: testsFilter.labels,
          not_labels: testsFilter.not_labels,
          labels_condition: testsFilter.labels_condition,
          last_status: testsFilter.statuses,
          search: testsFilter.name_or_id,
          plan: testsFilter.plans,
          suite: testsFilter.suites,
          assignee: testsFilter.assignee,
          test_plan_started_after: testsFilter.test_plan_started_after,
          test_plan_started_before: testsFilter.test_plan_started_before,
          test_plan_created_after: testsFilter.test_plan_created_after,
          test_plan_created_before: testsFilter.test_plan_created_before,
          test_created_after: testsFilter.test_created_after,
          test_created_before: testsFilter.test_created_before,
          _n: params._n,
        },
        false
      ).unwrap()

      const data = makeNode<Test | TestPlan>(res.results, params, (item) => ({
        isOpen: checkIsOpen(item, drawerTest),
        isLeaf: item.is_leaf,
      }))
      return { data, nextInfo: res.pages, _n: params._n }
    },
    [testsFilter, testsOrdering, drawerTest]
  )

  const fetcherAncestors = (id: NodeId) => {
    return getAncestors({ project: project.id, id: Number(id) }).unwrap()
  }

  const value = useMemo(() => {
    return {
      testsTree,
      fetcher,
      fetcherAncestors,
      skipInit: false,
    }
  }, [testsTree, fetcher, fetcherAncestors])

  return <TestsTreeContext.Provider value={value}>{children}</TestsTreeContext.Provider>
}
