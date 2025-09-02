import { Button, Spin } from "antd"
import classNames from "classnames"
import { useTranslation } from "react-i18next"

import { LazyNodeProps, LazyTreeNodeApi } from "../api"
import styles from "./styles.module.css"

interface Props<TData, TProps extends LazyNodeProps> {
  node?: LazyTreeNodeApi<TData, TProps>
  isLoading: boolean
  isRoot: boolean
  isLast: boolean
  onMore: () => Promise<void>
  offset?: number
  style?: React.CSSProperties
}

export const TreeBaseLoadMore = <TData, TProps extends LazyNodeProps>({
  node,
  isLoading,
  isRoot,
  isLast,
  offset: initOffset,
  style,
  onMore,
}: Props<TData, TProps>) => {
  const { t } = useTranslation()
  const nodeLevel = node ? node.props.level : 0
  const nodeTitle = node ? node.title : "root"
  const offset = !initOffset ? nodeLevel * 20 : initOffset

  if (isLoading) {
    return (
      <div
        id={`node-${nodeTitle}-load-more-spinner`}
        className={styles.container}
        style={{ paddingLeft: offset, ...style }}
      >
        <div
          className={classNames(styles.loadMore, {
            [styles.isRoot]: isRoot,
            [styles.isLast]: isLast,
          })}
        >
          <Spin size="small" />
        </div>
      </div>
    )
  }

  return (
    <div
      id={`node-${nodeTitle}-more`}
      className={styles.container}
      style={{ paddingLeft: offset, ...style }}
    >
      <div className={classNames(styles.loadMore, { [styles.isRoot]: isRoot })}>
        <Button id={`node-${nodeTitle}-more-btn`} size="small" type="link" onClick={onMore}>
          {t("Load more")}
        </Button>
      </div>
    </div>
  )
}
