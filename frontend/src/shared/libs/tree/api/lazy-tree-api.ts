import { LazyNodeProps, LazyTreeNodeApi } from "./lazy-tree-node-api"
import { TreeApi } from "./tree-api"
import { TreeNodeApi } from "./tree-node-api"
import { NodeId, OptsInitRoot, TreeFetcherAncestors, TreeNodeData, TreeNodeFetcher } from "./types"

interface Params<TData, TProps> {
  initData: TreeNodeData<TData, TProps>[]
  forceRerender: () => void
  fetcher: TreeNodeFetcher<TData, TProps>
  fetcherAncestors?: TreeFetcherAncestors
  initParent?: NodeId | null
  selectedId?: NodeId | null
  rootId?: NodeId | null
  skipInit?: boolean
  cacheKey?: string
}

export class LazyTreeApi<TData, TProps extends LazyNodeProps = LazyNodeProps> extends TreeApi<
  TData,
  TProps
> {
  public initLoading: boolean
  public hasMore: boolean
  public isMoreLoading: boolean
  public page: number
  public initParent: NodeId | null
  public rootId: NodeId | null
  public selectedId: NodeId | null
  public cacheKey: string | undefined
  public openedIds = new Set<NodeId>()
  public nonce: number
  // @ts-ignore
  declare public nodes: LazyTreeNodeApi<TData, TProps>[]
  public fetcher: Params<TData, TProps>["fetcher"]
  public fetcherAncestors: Params<TData, TProps>["fetcherAncestors"] | undefined
  private currentRequestId: string | undefined

  constructor({
    initData,
    fetcher,
    fetcherAncestors,
    forceRerender,
    initParent = null,
    cacheKey,
    selectedId = initParent,
    rootId = null,
  }: Params<TData, TProps>) {
    super(initData, forceRerender)
    this.fetcher = fetcher
    this.fetcherAncestors = fetcherAncestors
    this.selectedId = selectedId
    this.rootId = rootId
    this.initParent = initParent
    this.cacheKey = cacheKey
    this.nonce = 0
    this.page = 1
    this.isMoreLoading = false
    this.initLoading = true
    this.hasMore = true
    this.initStoreOpenId()
  }

  // @ts-ignore
  public createNode = (
    nodeData: TreeNodeData<TData, TProps>,
    parent: LazyTreeNodeApi<TData, TProps> | null = null
  ): LazyTreeNodeApi<TData, TProps> => {
    const node = new LazyTreeNodeApi<TData, TProps>({
      // @ts-ignore
      tree: this,
      id: nodeData.id,
      // @ts-ignore
      parent,
      data: nodeData.data,
      title: nodeData.title,
      props: nodeData.props,
      children: [],
    })
    if (nodeData.children) {
      node.addChildren(nodeData.children)
    }
    return node
  }

  public async refetchNodeBy(predicate: (node: LazyTreeNodeApi<TData, TProps>) => boolean) {
    const findedNode = this.findBy(
      predicate as unknown as (node: TreeNodeApi<TData, TProps>) => boolean
    ) as unknown as LazyTreeNodeApi<TData, TProps>
    if (!findedNode) {
      this.initRoot()
      return
    }

    findedNode.updateProps({ isLoading: true })
    const { data, nextInfo } = await this.fetcher({
      page: 1,
      level: findedNode.props.level + 1,
      parent: findedNode.id,
      _n: Date.now().toString(),
    })
    findedNode.updateChildren(() =>
      data.map((node) => ({
        ...node,
        props: { ...node.props, isOpen: this.openedIds.has(node.id) || node.props.isOpen },
      }))
    )
    findedNode.updateProps({ isLoading: false, isOpen: true, hasMore: nextInfo.next !== null })
    await this.loadChildrenRecursively(findedNode.children)
  }

  private getReqid() {
    return Date.now().toString()
  }

  public async initRoot(opts?: OptsInitRoot<TData, TProps>) {
    this.page = 1

    this.currentRequestId = this.getReqid()

    if (opts?.cacheKey) {
      this.cacheKey = opts.cacheKey
      this.initStoreOpenId()
    }

    if (opts?.fetcher) {
      this.fetcher = opts.fetcher
    }

    if (opts?.fetcherAncestors) {
      this.fetcherAncestors = opts.fetcherAncestors
    }

    if (opts?.initParent !== undefined) {
      this.initParent = opts?.initParent
    }

    this.initLoading = true

    const { data, nextInfo, _n } = await this.fetcher({
      page: 1,
      level: 0,
      parent: this.initParent,
      _n: this.currentRequestId,
    })

    let ancestors: number[] = []
    if (
      this.fetcherAncestors &&
      this.selectedId &&
      !data.some((node) => Number(node.id) === Number(this.selectedId))
    ) {
      if (_n !== this.currentRequestId) {
        return
      }

      ancestors = await this.fetcherAncestors(this.selectedId)

      if (_n !== this.currentRequestId) {
        return
      }
      this.setOpenIds(new Set(ancestors))
    }

    if (_n !== this.currentRequestId) {
      return
    }

    this.nodes = data.map((childNode) =>
      this.createNode(
        {
          ...childNode,
          props: {
            ...childNode.props,
            isOpen: this.openedIds.has(childNode.id) || childNode.props.isOpen,
          },
        },
        null
      )
    )
    this.hasMore = nextInfo.next !== null
    this.initLoading = false
    this.nonce += 1
    this.forceRerender()

    if (_n !== this.currentRequestId) {
      return
    }

    await this.loadChildrenRecursively(this.nodes)
  }

  public async loadMoreRootPage() {
    if (this.isMoreLoading) {
      return
    }
    this.isMoreLoading = true
    this.page += 1
    const { data, nextInfo } = await this.fetcher({
      page: this.page,
      level: 0,
      parent: this.initParent,
      _n: this.getReqid(),
    })

    this.nodes = [
      ...this.nodes,
      ...data.map((childNode) =>
        this.createNode(
          {
            ...childNode,
            props: {
              ...childNode.props,
              isOpen: this.openedIds.has(childNode.id) || childNode.props.isOpen,
            },
          },
          null
        )
      ),
    ]
    this.forceRerender()

    await this.loadChildrenRecursively(this.nodes)

    this.hasMore = nextInfo.next !== null
    this.isMoreLoading = false
  }

  public setOpenIds(openedIds: Set<NodeId>) {
    openedIds.forEach((id) => this.storeOpenId(id, true))
  }

  public storeOpenId(newOpenId: NodeId, toggle: boolean) {
    if (toggle) {
      if (!this.openedIds.has(newOpenId)) {
        this.openedIds.add(newOpenId)
        if (this.cacheKey) {
          localStorage.setItem(`${this.cacheKey}_openedIds`, JSON.stringify([...this.openedIds]))
        }
      }
    } else {
      if (this.openedIds.has(newOpenId)) {
        this.openedIds.delete(newOpenId)
        if (this.cacheKey) {
          localStorage.setItem(`${this.cacheKey}_openedIds`, JSON.stringify([...this.openedIds]))
        }
      }
    }
  }

  public openUpwards(node: TreeNodeApi<TData, TProps>) {
    let current: TreeNodeApi<TData, TProps> | null = node.parent
    while (current) {
      this.storeOpenId(current.id, true)
      current.props.isOpen = true
      current = current.parent
    }
    this.forceRerender()
  }

  public async updateSelectId(id: NodeId | null) {
    super.updateSelectId(id)
    if (!id) {
      return
    }

    const findNode = this.findById(id)
    if (findNode) {
      this.openUpwards(findNode)
      return
    }

    if (this.fetcherAncestors) {
      const ancestors = await this.fetcherAncestors(id)
      this.setOpenIds(new Set(ancestors))
      for (const openId of ancestors) {
        await this.refetchNodeBy((node) => node.id === openId)
      }
    }
  }

  protected initStoreOpenId() {
    if (this.cacheKey) {
      const openedIds = localStorage.getItem(`${this.cacheKey}_openedIds`)
      if (openedIds) {
        this.openedIds = new Set(JSON.parse(openedIds) as NodeId[])
      }
    }
  }

  protected async loadChildrenRecursively(nodes: LazyTreeNodeApi<TData, TProps>[]) {
    for (const node of nodes) {
      if (!node.props.isOpen || !node.props.canOpen) {
        continue
      }

      node.updateProps({ isLoading: true })
      const { data, nextInfo } = await this.fetcher({
        page: 1,
        level: node.props.level + 1,
        parent: Number(node.id),
        _n: this.getReqid(),
      })

      node.updateChildren(() =>
        data.map((childNode) => ({
          ...childNode,
          props: {
            ...childNode.props,
            isOpen: this.openedIds.has(childNode.id) || childNode.props.isOpen,
          },
        }))
      )
      node.updateProps({ isLoading: false, isOpen: true, hasMore: nextInfo.next !== null })
      await this.loadChildrenRecursively(node.children)
    }
  }
}
