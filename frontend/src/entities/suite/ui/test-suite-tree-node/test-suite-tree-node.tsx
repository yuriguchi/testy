import { Spin } from "antd"
import classNames from "classnames"
import dayjs from "dayjs"
import { Link, useSearchParams } from "react-router-dom"

import { useAppDispatch } from "app/hooks"

import { Label } from "entities/label/ui"

import { setDrawerTestCase } from "entities/test-case/model"

import { icons } from "shared/assets/inner-icons"
import { colors } from "shared/config"
import { LazyNodeProps, LazyTreeNodeApi } from "shared/libs/tree"
import { ArchivedTag, TreeTableLoadMore } from "shared/ui"

import styles from "./styles.module.css"

const { ArrowIcon } = icons

const getLink = (
  node: LazyTreeNodeApi<Suite | TestCase, LazyNodeProps>,
  projectId: number,
  testSuiteId?: string | null
) => {
  const queryParams = new URLSearchParams(location.search)

  if (!node.props.isLeaf) {
    return `/projects/${projectId}/suites/${node.id}?${queryParams.toString()}`
  }

  queryParams.set("test_case", String(node.id))
  return `/projects/${projectId}/suites/${testSuiteId ?? (node.data as TestCase).suite.id}?${queryParams.toString()}`
}

interface Props {
  node: LazyTreeNodeApi<Suite | TestCase, LazyNodeProps>
  projectId: number
  visibleColumns: ColumnParam[]
  testSuiteId?: string | null
}

export const TestSuiteTreeNode = ({ node, visibleColumns, projectId, testSuiteId }: Props) => {
  const [searchParams] = useSearchParams()
  const dispatch = useAppDispatch()

  const offset = node.props.level * 20 + 8
  const isSelected = searchParams.get("test_case") === String(node.id) && node.props.isLeaf
  const data = node.data as Suite
  const isVisible = (key: string) => visibleColumns.some((i) => i.key === key)
  const link = getLink(node, projectId, testSuiteId)

  const handleMoreClick = async () => {
    await node.more()
  }

  return (
    <>
      <tr
        id={`${node.title}-${node.id}`}
        className={classNames(styles.tr, { [styles.active]: isSelected })}
      >
        {isVisible("name") && (
          <td className={styles.containerItem}>
            <span style={{ width: offset, height: 1, float: "left" }} />
            <div className={styles.nodeLeftAction}>
              {node.props.isLeaf && (node.data as TestCase).is_archive && <ArchivedTag />}
              {node.props.isLoading && <Spin size="small" className={styles.loader} />}
              {!node.props.isLoading && node.props.canOpen && (
                <ArrowIcon
                  width={24}
                  height={24}
                  className={classNames(styles.arrowIcon, {
                    [styles.arrowIconOpen]: node.props.isOpen,
                  })}
                  onClick={(e) => {
                    // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
                    e.stopPropagation()
                    node.open()
                  }}
                />
              )}
            </div>
            <Link
              to={link}
              className={classNames(styles.name, {
                [styles.entityName]: !node.props.isLeaf,
                [styles.activeLink]: isSelected,
              })}
              onClick={(e) => {
                e.stopPropagation()
                if (node.props.isLeaf) {
                  dispatch(setDrawerTestCase(node.data as TestCase))
                }
              }}
            >
              {node.data.name}
            </Link>
          </td>
        )}
        {isVisible("id") && <td className={styles.containerItem}>{node.id}</td>}
        {isVisible("labels") && (
          <td className={styles.containerItem}>
            <ul className={styles.list}>
              {node.props.isLeaf &&
                (node.data as TestCase).labels.map((label, index) => (
                  <li key={index}>
                    <Label content={label.name} color={colors.accent} />
                  </li>
                ))}
            </ul>
          </td>
        )}
        {isVisible("estimate") && (
          <td className={styles.containerItem}>
            {data.estimates ?? (node.data as TestCase).estimate ?? "-"}
          </td>
        )}
        {isVisible("created_at") && (
          <td className={styles.containerItem}>
            {dayjs(data.created_at).format("YYYY-MM-DD HH:mm")}
          </td>
        )}
      </tr>
      {node.parent?.props.hasMore && node.isLast && (
        <TreeTableLoadMore
          isLoading={node.props.isMoreLoading}
          node={node}
          onMore={handleMoreClick}
          isLast={node.isLast}
          isRoot
          offset={offset}
        />
      )}
    </>
  )
}
