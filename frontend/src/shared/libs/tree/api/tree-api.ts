import { TreeNodeApi } from "./tree-node-api"
import { BaseTreeNodeProps, NodeId, TreeNodeData } from "./types"

export class TreeApi<TData, TProps extends BaseTreeNodeProps = BaseTreeNodeProps> {
  public nodes: TreeNodeApi<TData, TProps>[] = []
  public selectedId: NodeId | null = null
  public rootId: NodeId | null = null

  constructor(
    public initialNodes: TreeNodeData<TData, TProps>[] = [],
    public forceRerender: () => void
  ) {
    this.nodes = initialNodes.map((i) => this.createNode(i, null))
  }

  public createNode(
    nodeData: TreeNodeData<TData, TProps>,
    parent: TreeNodeApi<TData, TProps> | null = null
  ): TreeNodeApi<TData, TProps> {
    const node = new TreeNodeApi<TData, TProps>({
      // @ts-ignore
      tree: this,
      id: nodeData.id,
      parent,
      data: nodeData.data,
      title: nodeData.title,
      children: [],
      props: nodeData.props,
    })
    if (nodeData.children) {
      node.children = nodeData.children.map((childNode) => this.createNode(childNode, node))
    }
    return node
  }

  public removeById(id: NodeId) {
    const removeNode = (nodes: TreeNodeApi<TData, TProps>[]) => {
      for (let i = 0; i < nodes.length; i++) {
        if (nodes[i].id === id) {
          nodes.splice(i, 1)
          return true
        }
        if (nodes[i].children.length) {
          if (removeNode(nodes[i].children)) {
            return true
          }
        }
      }
      return false
    }

    return removeNode(this.nodes)
  }

  public updateById(id: NodeId, target: TreeNodeApi<TData, TProps>) {
    for (const node of this.preOrderTraversal()) {
      if (node.id === id) {
        Object.assign(node, target)
        return true
      }
    }
    return false
  }

  public findById(id: NodeId) {
    for (const node of this.preOrderTraversal()) {
      if (node.id === Number(id)) {
        return node
      }
    }
    return null
  }

  public findBy(predicate: (node: TreeNodeApi<TData, TProps>) => boolean) {
    for (const node of this.preOrderTraversal()) {
      if (predicate(node)) {
        return node
      }
    }
    return null
  }

  public filterBy(predicate: (node: TreeNodeApi<TData, TProps>) => boolean) {
    const result: TreeNodeApi<TData, TProps>[] = []
    for (const node of this.preOrderTraversal()) {
      if (predicate(node)) {
        result.push(node)
      }
    }
    return result
  }

  public updateSelectId(id: NodeId | null) {
    this.selectedId = id
    this.forceRerender()
  }

  public updateRootId(id: NodeId | null) {
    this.rootId = id
    this.forceRerender()
  }

  public closeAll() {
    for (const node of this.preOrderTraversal()) {
      if (node.props.isOpen) {
        node.close()
      }
    }
  }

  protected *preOrderTraversal(nodes = this.nodes): Generator<TreeNodeApi<TData, TProps>> {
    for (const node of nodes) {
      yield node
      if (node.children.length) {
        yield* this.preOrderTraversal(node.children)
      }
    }
  }
}
