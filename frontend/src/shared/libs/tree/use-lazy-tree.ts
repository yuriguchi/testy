import { DependencyList, useEffect, useMemo, useReducer } from "react"

import {
  LazyNodeProps,
  LazyTreeApi,
  NodeId,
  TreeFetcherAncestors,
  TreeNodeData,
  TreeNodeFetcher,
} from "./api"

export interface UseLazyTreeProps<TData, TProps> {
  fetcher: TreeNodeFetcher<TData, TProps>
  fetcherAncestors?: TreeFetcherAncestors
  initData?: TreeNodeData<TData, TProps>[]
  additionalFetchParams?: Record<string, unknown>
  initDependencies?: DependencyList
  initParent?: NodeId | null
  selectedId?: NodeId | null
  rootId?: NodeId | null
  skipInit?: boolean
  cacheKey?: string
}

export const useLazyTree = <TData, TProps extends LazyNodeProps>({
  initData,
  fetcher,
  fetcherAncestors,
  initDependencies = [],
  initParent,
  skipInit,
  cacheKey,
  selectedId,
  rootId,
}: UseLazyTreeProps<TData, TProps>) => {
  const [, forceRerender] = useReducer((x: number) => x + 1, 0)

  const tree = useMemo(() => {
    return new LazyTreeApi<TData, LazyNodeProps>({
      initData: initData ?? [],
      initParent,
      fetcher,
      fetcherAncestors,
      forceRerender,
      cacheKey,
      selectedId,
      rootId,
    })
  }, [])

  useEffect(() => {
    if (skipInit) {
      return
    }

    tree.initRoot({ fetcher, fetcherAncestors, initParent, cacheKey })
  }, [...initDependencies, initParent, skipInit, cacheKey])

  useEffect(() => {
    tree.updateSelectId(selectedId ?? null)
  }, [selectedId])

  useEffect(() => {
    tree.updateRootId(rootId ?? null)
  }, [rootId])

  return tree
}
