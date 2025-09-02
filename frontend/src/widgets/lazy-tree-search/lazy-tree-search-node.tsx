import { Spin } from "antd"
import classNames from "classnames"
import { MouseEvent } from "react"

import { icons } from "shared/assets/inner-icons"
import { LazyNodeProps, LazyTreeNodeApi, NodeId, TreeBaseLoadMore } from "shared/libs/tree"
import { HighLighterTesty } from "shared/ui"

import styles from "./styles.module.css"

const { ArrowIcon } = icons

interface Props {
  node: LazyTreeNodeApi<unknown, LazyNodeProps>
  onSelect: (node: LazyTreeNodeApi<unknown, LazyNodeProps> | null) => void
  selectedId?: NodeId | null
  searchText: string
}

export const LazyTreeSearchNode = ({ node, selectedId, searchText, onSelect }: Props) => {
  const offset = node.props.level * 20

  const handleOpenClick = async (e: MouseEvent<HTMLElement | SVGElement>) => {
    e.stopPropagation()
    await node.open()
  }

  const handleMoreClick = async () => {
    await node.more()
  }

  const handleSelect = () => {
    if (node.tree.selectedId === node.id) {
      node.tree.updateSelectId(null)
      onSelect(null)
      return
    }
    node.tree.updateSelectId(node.id)
    onSelect(node)
  }

  return (
    <>
      <div
        id={`${node.title}-${node.id}`}
        key={`${node.title}-${node.id}-treeview-suite`}
        style={{ paddingLeft: offset }}
      >
        <div
          className={classNames(styles.nodeBody, {
            [styles.activeNode]: selectedId === node.id,
            [styles.isRoot]: node.isRoot,
            [styles.isLast]: node.isLast,
          })}
          onClick={handleSelect}
        >
          <div className={styles.nodeLeftAction}>
            {node.props.isLoading && <Spin size="small" className={styles.loader} />}
            {!node.props.isLoading && node.props.canOpen && (
              <ArrowIcon
                className={classNames(styles.arrowIcon, {
                  [styles.arrowIconOpen]: node.props.isOpen,
                })}
                onClick={handleOpenClick}
              />
            )}
          </div>
          <HighLighterTesty searchWords={searchText} textToHighlight={node.title} />
        </div>
      </div>
      {node.parent?.props.hasMore && node.isLast && (
        <TreeBaseLoadMore
          isLoading={node.parent.props.isLoading}
          node={node}
          onMore={handleMoreClick}
          isRoot={node.isRoot}
          isLast={node.isLast}
        />
      )}
    </>
  )
}
