import { useContext } from "react"

import { useAppSelector } from "app/hooks"

import { selectFilter, selectOrdering, selectSettings } from "entities/test/model"

import { TestPlanTreeNodeView } from "entities/test-plan/ui"

import { ProjectContext } from "pages/project"

import { LazyNodeProps, LazyTreeNodeApi, LazyTreeView } from "shared/libs/tree"
import { TreeTable, TreeTableLoadMore } from "shared/ui"

import { TestsTreeContext } from "./tests-tree-provider"

interface Props {
  testPlanId?: number | null
}

export const TREE_KEY = "tests-tree"

export const TestsTree = ({ testPlanId = null }: Props) => {
  const { project } = useContext(ProjectContext)!
  const { testsTree, skipInit, fetcher, fetcherAncestors } = useContext(TestsTreeContext)!

  const testsFilter = useAppSelector(selectFilter)
  const testsOrdering = useAppSelector(selectOrdering)
  const testsTreeSettings = useAppSelector(selectSettings<TestTreeParams>("tree"))

  return (
    <TreeTable visibleColumns={testsTreeSettings.visibleColumns}>
      <LazyTreeView
        // @ts-ignore // TODO fix forward ref type
        ref={testsTree}
        cacheKey={`${project.id}-tests-tree`}
        fetcher={fetcher}
        fetcherAncestors={fetcherAncestors}
        initParent={testPlanId}
        initDependencies={[testsFilter, testsOrdering]}
        skipInit={skipInit}
        rootId={testPlanId}
        renderNode={(node) => (
          <TestPlanTreeNodeView
            node={node as LazyTreeNodeApi<Test | TestPlan, LazyNodeProps>} // FIX IT cast type
            visibleColumns={testsTreeSettings.visibleColumns}
            projectId={project.id}
            testPlanId={testPlanId}
          />
        )}
        renderLoadMore={({ isLoading, onMore }) => (
          <TreeTableLoadMore isLast isRoot isLoading={isLoading} onMore={onMore} />
        )}
      />
    </TreeTable>
  )
}
