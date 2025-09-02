import { Checkbox, Spin } from "antd"
import { CheckboxChangeEvent } from "antd/es/checkbox"
import classNames from "classnames"

import { icons } from "shared/assets/inner-icons"
import { LazyNodeProps, LazyTreeNodeApi, TreeBaseLoadMore } from "shared/libs/tree"

import styles from "./styles.module.css"

const { ArrowIcon } = icons

interface Props {
  node: LazyTreeNodeApi<Suite, LazyNodeProps>
  onCheck: (id: number) => void
}

export const SelectSuitesNode = ({ node, onCheck }: Props) => {
  const offset = node.props.level * 20

  const handleCheck = (e: CheckboxChangeEvent) => {
    onCheck(Number(node.id))
    const toggle = e.target.checked
    if (toggle) {
      node.check()
    } else {
      node.uncheck()
    }
  }

  const handleOpenClick = async () => {
    await node.open()
  }

  const handleMoreClick = async () => {
    await node.more()
  }

  return (
    <>
      <div id={`${node.title}-${node.id}`} style={{ paddingLeft: offset }}>
        <div
          className={classNames(styles.nodeBody, {
            [styles.isRoot]: node.isRoot,
            [styles.isLast]: node.isLast,
          })}
        >
          <div className={styles.nodeLeftAction}>
            <Checkbox
              style={{ height: 16 }}
              checked={node.props.isChecked}
              onChange={handleCheck}
              onClick={(e) => e.stopPropagation()}
              indeterminate={node.props.isHalfChecked && !node.props.isChecked}
            />
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
          <span>{node.data.name}</span>
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
