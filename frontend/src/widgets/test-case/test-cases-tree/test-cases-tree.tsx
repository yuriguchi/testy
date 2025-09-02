import { useContext } from "react"
import { useParams } from "react-router-dom"

import { useAppSelector } from "app/hooks"

import { TestSuiteTreeNode } from "entities/suite/ui"

import { selectFilter, selectOrdering, selectSettings } from "entities/test-case/model"

import { ProjectContext } from "pages/project"

import { LazyNodeProps, LazyTreeNodeApi, LazyTreeView } from "shared/libs/tree"
import { TreeTable, TreeTableLoadMore } from "shared/ui"

import { TestCasesTreeContext } from "./test-cases-tree-provider"

export const TestsCasesTree = () => {
  const { testSuiteId = null } = useParams<ParamTestSuiteId>()
  const { project } = useContext(ProjectContext)!
  const { testCasesTree, skipInit, fetcher, fetcherAncestors } = useContext(TestCasesTreeContext)!

  const testCasesTreeSettings = useAppSelector(selectSettings<TestTreeParams>("tree"))
  const testCasesTreeFilter = useAppSelector(selectFilter)
  const testCasesTreeOrdering = useAppSelector(selectOrdering)

  return (
    <TreeTable visibleColumns={testCasesTreeSettings.visibleColumns}>
      <LazyTreeView
        // @ts-ignore // TODO fix forward ref type
        ref={testCasesTree}
        cacheKey={`${project.id}-test-cases-tree`}
        fetcher={fetcher}
        fetcherAncestors={fetcherAncestors}
        initParent={testSuiteId}
        initDependencies={[testCasesTreeFilter, testCasesTreeOrdering]}
        skipInit={skipInit}
        rootId={testSuiteId}
        renderNode={(node) => (
          <TestSuiteTreeNode
            node={node as LazyTreeNodeApi<Suite | TestCase, LazyNodeProps>} // FIX IT cast type
            visibleColumns={testCasesTreeSettings.visibleColumns}
            projectId={project.id}
            testSuiteId={testSuiteId}
          />
        )}
        renderLoadMore={({ isLoading, onMore }) => (
          <TreeTableLoadMore isLast isRoot isLoading={isLoading} onMore={onMore} />
        )}
      />
    </TreeTable>
  )
}
