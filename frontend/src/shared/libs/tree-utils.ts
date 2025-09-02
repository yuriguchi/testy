interface Data<T> {
  id: Id
  key: string
  name: string
  children?: T[]
  title: string
}

interface Node<T> {
  id?: number
  children: T[]
}

interface FilterRowsOptions {
  isAllExpand?: boolean
  isShowChildren?: boolean
}

export class TreeUtils {
  static deleteChildren = <T extends { children?: T[] }>(arr: T[]): T[] => {
    const childs = arr
    for (let i: number = childs.length; i--; i > 0) {
      if (childs[i].children) {
        if (childs[i].children?.length) {
          TreeUtils.deleteChildren(childs[i].children ?? [])
        } else {
          delete childs[i].children
        }
      }
    }
    return arr
  }

  static deleteNode = <T extends Node<T>>(arr: T[], nodeId: Id): T[] => {
    return arr
      .filter((node) => {
        return node.id !== nodeId
      })
      .map((node) => {
        if (node.children.length !== 0) {
          return {
            ...node,
            children: TreeUtils.deleteNode(node.children, nodeId),
          }
        }
        return node
      })
  }

  static filterRows<T extends Data<T>>(
    tableRows: T[],
    searchText: string,
    options: FilterRowsOptions = {
      isAllExpand: true,
      isShowChildren: true,
    }
  ): [T[], string[] | number[]] {
    const searchTextLower = searchText.toLowerCase()

    const filterNodes = (result: T[], currentNode: T): T[] => {
      const titleLower = currentNode.title.toLowerCase()

      if (titleLower.includes(searchTextLower) && !currentNode.children?.length) {
        result.push(currentNode)
        return result
      }

      if (currentNode.children?.length) {
        const nodes = currentNode.children.reduce(filterNodes, [])

        if (nodes.length) {
          result.push({
            ...currentNode,
            children: nodes,
          })
        } else if (titleLower.includes(searchTextLower)) {
          result.push({
            ...currentNode,
            children: options.isShowChildren ? currentNode.children : [],
          })
        }
      }

      return result
    }

    const expandRows = (result: string[], currentRow: T): string[] => {
      const titleLower = currentRow.title.toLowerCase()

      if (titleLower.includes(searchTextLower) && !currentRow.children?.length) {
        result.push(String(currentRow.key))
        return result
      }

      if (currentRow.children?.length) {
        const nodes = currentRow.children.reduce(expandRows, [])
        // if need expand result push
        // if need no expand just return result
        if (!nodes.length) {
          if (options.isAllExpand) result.push(String(currentRow.key))
          return result
        }
        result.push(String(currentRow.key), ...nodes)
      }

      return result
    }

    const filteredRows = tableRows.reduce(filterNodes, [])
    const expandedRows = filteredRows.reduce(expandRows, [])

    return [filteredRows, expandedRows]
  }
}
