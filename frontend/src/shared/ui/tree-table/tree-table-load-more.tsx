import { Button, Spin } from "antd"
import classNames from "classnames"
import { useTranslation } from "react-i18next"

import { LazyNodeProps, LazyTreeNodeApi } from "shared/libs/tree"

import styles from "./styles.module.css"

interface Props<TData, TProps extends LazyNodeProps> {
  node?: LazyTreeNodeApi<TData, TProps>
  isLoading: boolean
  isRoot: boolean
  isLast: boolean
  onMore: () => Promise<void>
  offset?: number
}

export const TreeTableLoadMore = <TData, TProps extends LazyNodeProps>({
  node,
  isLoading,
  isRoot,
  isLast,
  offset: initOffset,
  onMore,
}: Props<TData, TProps>) => {
  const { t } = useTranslation()
  const nodeLevel = node ? node.props.level : 0
  const nodeTitle = node ? node.title : "root"
  const offset = !initOffset ? nodeLevel * 20 : initOffset

  if (isLoading) {
    return (
      <tr id={`node-${nodeTitle}-load-more-spinner`} className={styles.loadMoreContainer}>
        <td
          colSpan={100}
          className={classNames(styles.loadMore, {
            [styles.isRoot]: isRoot,
            [styles.isLast]: isLast,
          })}
        >
          <span style={{ width: offset, height: 1, float: "left" }} />
          <Spin size="small" />
        </td>
      </tr>
    )
  }

  return (
    <tr id={`node-${nodeTitle}-more`} className={styles.loadMoreContainer}>
      <td colSpan={100} className={classNames(styles.loadMore, { [styles.isRoot]: isRoot })}>
        <span style={{ width: offset, height: 1, float: "left" }} />
        <Button id={`node-${nodeTitle}-more-btn`} size="small" type="link" onClick={onMore}>
          {t("Load more")}
        </Button>
      </td>
    </tr>
  )
}
