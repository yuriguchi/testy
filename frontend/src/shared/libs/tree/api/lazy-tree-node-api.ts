import { LazyTreeApi } from "./lazy-tree-api"
import { TreeNodeApi } from "./tree-node-api"
import { BaseTreeNodeProps, NodeId } from "./types"

export interface LazyNodeProps extends BaseTreeNodeProps {
  isLoading: boolean
  isMoreLoading: boolean
  hasMore: boolean
  page: number
}

interface LazyTreeNodeApiParams<TData, TProps extends LazyNodeProps> {
  tree: LazyTreeApi<TData, TProps>
  id: NodeId
  parent: LazyTreeNodeApi<TData, TProps> | null
  data: TData
  title: string
  children: LazyTreeNodeApi<TData, TProps>[]
  props: TProps
}

export class LazyTreeNodeApi<TData, TProps extends LazyNodeProps> extends TreeNodeApi<
  TData,
  LazyNodeProps
> {
  public tree: LazyTreeApi<TData, TProps>
  public fetcher: LazyTreeApi<TData, TProps>["fetcher"]
  public props: TProps
  public children: LazyTreeNodeApi<TData, TProps>[] = []

  constructor(params: LazyTreeNodeApiParams<TData, TProps>) {
    super(params)
    this.tree = params.tree
    this.fetcher = params.tree.fetcher
    this.props = params.props
  }

  public async open() {
    if (this.props.isOpen) {
      this.close()
      return
    }

    const findNodeInTree = this.tree.findById(this.id)
    this.tree.storeOpenId(this.id, true)
    if (!findNodeInTree?.children.length) {
      this.updateProps({ isLoading: true })
      const { data, nextInfo } = await this.fetcher({
        page: 1,
        level: this.props.level + 1,
        parent: this.id,
      })
      this.updateChildren(() => data)
      this.updateProps({ isLoading: false, hasMore: nextInfo.next !== null })
    }
    super.open()
  }

  public close() {
    this.tree.storeOpenId(this.id, false)
    super.close()
  }

  public async more() {
    const getMoreChild = this.fetcher({
      page: this.props.page + 1,
      level: this.props.level,
      parent: this.parent ? this.parent.id : null,
    })

    if (this.parent) {
      this.parent.updateProps({ isLoading: true })
      this.updateProps({ isMoreLoading: true })
      const { data, nextInfo } = await getMoreChild

      this.parent.addChildren(data)
      this.parent.updateProps({ isLoading: false, hasMore: nextInfo.next !== null })
      this.updateProps({ isMoreLoading: false })
    }
  }

  public async refetch() {
    this.updateProps({ isLoading: true })
    const { data, nextInfo } = await this.fetcher({
      page: 1,
      level: this.props.level,
      parent: this.parent ? this.parent.id : null,
    })
    this.updateChildren(() => data)
    this.updateProps({ isLoading: false, hasMore: nextInfo.next !== null })
  }

  public updateProps(target: Partial<LazyNodeProps>, isTriggerRerender = true) {
    Object.assign(this.props, target)

    if (isTriggerRerender) {
      this.tree.forceRerender()
    }
  }
}
