import { Empty } from "antd"
import { ForwardedRef, Fragment, forwardRef, useImperativeHandle } from "react"

import { ContainerLoader } from "shared/ui"

import { LazyNodeProps, LazyTreeApi, LazyTreeNodeApi } from "../api"
import { UseLazyTreeProps, useLazyTree } from "../use-lazy-tree"
import { TreeBaseLoadMore } from "./tree-base-load-more"

interface Props<TData, TProps extends LazyNodeProps> extends UseLazyTreeProps<TData, TProps> {
  renderNode: (node: LazyTreeNodeApi<TData, TProps>) => JSX.Element
  renderLoadMore?: ({
    onMore,
    isLoading,
  }: {
    isLoading: boolean
    onMore: () => Promise<void>
  }) => JSX.Element
}

interface PapaViewListProps<TData, TProps extends LazyNodeProps> {
  nodes: LazyTreeNodeApi<TData, TProps>[]
  renderNode: (node: LazyTreeNodeApi<TData, TProps>) => JSX.Element
}

const TREE_VIEW_LIST_NO_DATA_HEIGHT = 162

const TreeViewList = <TData, TProps extends LazyNodeProps>({
  nodes,
  renderNode,
}: PapaViewListProps<TData, TProps>) => {
  return nodes.map((node) => (
    <Fragment key={`${node.title}-${node.id}`}>
      {renderNode(node)}
      {node.props.isOpen && !!node.children.length && (
        <TreeViewList
          nodes={node.children as unknown as LazyTreeNodeApi<TData, TProps>[]}
          renderNode={renderNode}
        />
      )}
    </Fragment>
  ))
}

// eslint-disable-next-line comma-spacing
const TreeViewComponent = <TData,>(
  props: Props<TData, LazyNodeProps>,
  ref: ForwardedRef<LazyTreeApi<TData, LazyNodeProps> | undefined>
) => {
  const tree = useLazyTree<TData, LazyNodeProps>(props)

  useImperativeHandle(ref, () => tree)

  const handleLoadMore = async () => {
    await tree.loadMoreRootPage()
  }

  if (tree.initLoading) {
    return (
      <div style={{ height: TREE_VIEW_LIST_NO_DATA_HEIGHT }}>
        <div id="loader-init">
          <ContainerLoader />
        </div>
      </div>
    )
  }

  if (!tree.nodes.length && !tree.initLoading) {
    return (
      <div style={{ height: TREE_VIEW_LIST_NO_DATA_HEIGHT }}>
        <div id="empty-init">
          <Empty style={{ margin: "16px 0" }} />
        </div>
      </div>
    )
  }

  return (
    <>
      <TreeViewList nodes={tree.nodes} renderNode={props.renderNode} />
      {tree.hasMore &&
        (!props.renderLoadMore ? (
          <TreeBaseLoadMore isLast isLoading={tree.isMoreLoading} isRoot onMore={handleLoadMore} />
        ) : (
          props.renderLoadMore({ onMore: handleLoadMore, isLoading: tree.isMoreLoading })
        ))}
    </>
  )
}

export const LazyTreeView = forwardRef(TreeViewComponent)
