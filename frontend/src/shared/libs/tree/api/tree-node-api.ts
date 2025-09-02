import { TreeApi } from "./tree-api"
import { BaseTreeNodeProps, NodeId, TreeNodeApiParams, TreeNodeData } from "./types"

export class TreeNodeApi<TData, TProps extends BaseTreeNodeProps = BaseTreeNodeProps> {
  tree: TreeApi<TData, TProps>
  id: NodeId
  parent: TreeNodeApi<TData, TProps> | null
  data: TData
  title: string
  children: TreeNodeApi<TData, TProps>[]
  props: TProps

  constructor(params: TreeNodeApiParams<TData, TProps>) {
    this.tree = params.tree
    this.id = params.id
    this.parent = params.parent
    this.data = params.data
    this.title = params.title
    this.children = params.children
    this.props = params.props
  }

  get isRoot() {
    return !this.parent
  }

  get isLast() {
    return this.id === this.parent?.children[this.parent?.children.length - 1]?.id
  }

  public open() {
    this.props.isOpen = true
    this.tree.forceRerender()
  }

  public close() {
    this.props.isOpen = false
    this.tree.forceRerender()
  }

  public select() {
    this.props.isSelected = true
    this.tree.forceRerender()
  }

  public unselect() {
    this.props.isSelected = false
    this.tree.forceRerender()
  }

  public update(target: Partial<TreeNodeApi<TData, TProps>>) {
    Object.assign(this, target)
    this.tree.forceRerender()
  }

  public check() {
    this.props.isChecked = true
    // @ts-ignore
    this.updatePropsRecursiveUp({ isHalfChecked: true }, (node) => {
      return node.children.some((n) => n.props.isChecked ?? n.props.isHalfChecked)
    })
  }

  public uncheck() {
    const countCheckedParentChild =
      this.parent?.getRecursiveChildrenBy((node) => node.props.isChecked ?? false).length ?? 0
    const countCheckedChild =
      this.getRecursiveChildrenBy((node) => node.props.isChecked ?? false).length ?? 0

    // @ts-ignore
    this.updateProps({ isChecked: false, isHalfChecked: !!countCheckedChild || false })

    // last check in group
    if (countCheckedParentChild === 1) {
      this.parent?.updatePropsRecursiveUp(
        // @ts-ignore
        { isHalfChecked: false },
        (node) => !node.children.some((n) => n.props.isChecked ?? n.props.isHalfChecked)
      )
    }
  }

  public updateProps(target: Partial<TProps>, isTriggerRerender = true) {
    Object.assign(this.props, target)
    if (isTriggerRerender) {
      this.tree.forceRerender()
    }
  }

  public addChildren(newChildren: TreeNodeData<TData, TProps>[]) {
    this.children = [
      ...this.children,
      ...newChildren.map((child) => this.tree.createNode(child, this)),
    ]
    this.tree.forceRerender()
  }

  public updateChildren(
    updateFn: (newChildren: TreeNodeData<TData, TProps>[]) => TreeNodeData<TData, TProps>[]
  ) {
    this.children = [...updateFn(this.children as TreeNodeData<TData, TProps>[])].map((child) =>
      this.tree.createNode(child, this)
    )
    this.tree.forceRerender()
  }

  public updatePropsRecursiveDown(
    target: Partial<TProps>,
    predicate: (node: TreeNodeApi<TData, TProps>) => boolean
  ) {
    for (const node of this.preOrderTraversal([this])) {
      if (predicate(node)) {
        node.updateProps(target, false)
      }
    }
    this.tree.forceRerender()
  }

  public updatePropsRecursiveUp(
    target: Partial<TProps>,
    predicate: (node: TreeNodeApi<TData, TProps>) => boolean
  ) {
    if (predicate(this)) {
      this.updateProps(target, false)
    }

    if (this.parent) {
      this.parent.updatePropsRecursiveUp(target, predicate)
    }
    this.tree.forceRerender()
  }

  public getChildrenBy(filterFn: (node: TreeNodeApi<TData, TProps>) => boolean) {
    return this.children.filter(filterFn)
  }

  public getRecursiveChildrenBy(filterFn: (node: TreeNodeApi<TData, TProps>) => boolean) {
    const result: TreeNodeApi<TData, TProps>[] = []
    for (const node of this.preOrderTraversal(this.children)) {
      if (filterFn(node)) {
        result.push(node)
      }
    }
    return result
  }

  private *preOrderTraversal(
    nodes: TreeNodeApi<TData, TProps>[] = [this]
  ): Generator<TreeNodeApi<TData, TProps>> {
    for (const childNode of nodes) {
      yield childNode
      if (childNode.children.length) {
        yield* this.preOrderTraversal(childNode.children)
      }
    }
  }
}
