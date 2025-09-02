import { TreeApi } from "./tree-api"
import { TreeNodeApi } from "./tree-node-api"

export type NodeId = number | string
export interface BaseTreeNodeProps {
  level: number
  isLeaf: boolean
  isOpen: boolean
  canOpen: boolean
  isChecked?: boolean
  isHalfChecked?: boolean
  isSelected?: boolean
}

export interface TreeNodeData<TData, TProps> {
  id: NodeId
  parent: NodeId | null
  title: string
  data: TData
  children: TreeNodeData<TData, TProps>[]
  props: TProps
}

export interface TreeNodeApiParams<TData, TProps extends BaseTreeNodeProps> {
  tree: TreeApi<TData, TProps>
  id: NodeId
  parent: TreeNodeApi<TData, TProps> | null
  data: TData
  title: string
  children: TreeNodeApi<TData, TProps>[]
  props: TProps
}

export interface TreeBaseFetcherParams {
  page: number
  level: number
  parent?: NodeId | null
  _n?: string
}

export interface OptsInitRoot<TData, TProps> {
  fetcher?: TreeNodeFetcher<TData, TProps>
  fetcherAncestors?: TreeFetcherAncestors
  initParent?: NodeId | null
  cacheKey?: string
}

export type TreeNodeFetcher<TData, TProps> = (
  params: TreeBaseFetcherParams,
  additionalParams?: Record<string, unknown>
) => Promise<{
  data: TreeNodeData<TData, TProps>[]
  nextInfo: PaginationResponsePages
  _n?: string
}>

export type TreeFetcherAncestors = (id: NodeId) => Promise<number[]>
