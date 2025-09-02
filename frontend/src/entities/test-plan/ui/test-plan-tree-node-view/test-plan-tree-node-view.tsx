import { Spin } from "antd"
import classNames from "classnames"
import dayjs from "dayjs"
import { useTranslation } from "react-i18next"
import { Link } from "react-router-dom"

import { useAppDispatch, useAppSelector } from "app/hooks"

import { Label } from "entities/label/ui"

import { selectDrawerTest, setDrawerTest } from "entities/test/model"

import { UserAvatar, UserUsername } from "entities/user/ui"

import { icons } from "shared/assets/inner-icons"
import { colors } from "shared/config"
import { LazyNodeProps, LazyTreeNodeApi } from "shared/libs/tree"
import { ArchivedTag, Status, TreeTableLoadMore } from "shared/ui"
import { UntestedStatus } from "shared/ui/status"

import styles from "./styles.module.css"

const { ArrowIcon } = icons

const getLink = (
  node: LazyTreeNodeApi<Test | TestPlan, LazyNodeProps>,
  projectId: number,
  testPlanId?: number | null
) => {
  const queryParams = new URLSearchParams(location.search)

  if (!node.props.isLeaf) {
    return `/projects/${projectId}/plans/${node.id}?${queryParams.toString()}`
  }

  queryParams.set("test", String(node.id))
  return `/projects/${projectId}/plans/${testPlanId ?? ""}?${queryParams.toString()}`
}

interface Props {
  node: LazyTreeNodeApi<Test | TestPlan, LazyNodeProps>
  visibleColumns: ColumnParam[]
  projectId: number
  testPlanId?: number | null
}

export const TestPlanTreeNodeView = ({ node, visibleColumns, projectId, testPlanId }: Props) => {
  const { t } = useTranslation()
  const dispatch = useAppDispatch()
  const drawerTest = useAppSelector(selectDrawerTest)

  const data = node.data as unknown as TestPlan
  const offset = node.props.level * 20 + 8
  const isSelected =
    (testPlanId === node.id && !node.props.isLeaf) ||
    (String(drawerTest?.id) === String(node.id) && node.props.isLeaf)
  const link = getLink(node, projectId, testPlanId)
  const isVisible = (key: string) => visibleColumns.some((i) => i.key === key)

  const handleMoreClick = async () => {
    await node.more()
  }

  return (
    <>
      <tr
        id={`${node.title}-${node.id}`}
        className={classNames(styles.tr, {
          [styles.active]: isSelected,
        })}
      >
        {isVisible("name") && (
          <td className={styles.containerItem}>
            <span style={{ width: offset, height: 1, float: "left" }} />
            <div className={styles.nodeLeftAction}>
              {data.is_archive && <ArchivedTag />}
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
                  dispatch(setDrawerTest(node.data as Test))
                }
              }}
            >
              {!node.props.isLeaf ? node.data.title : node.data.name}
            </Link>
          </td>
        )}
        {isVisible("last_status") && (
          <td className={styles.containerItem}>
            {node.props.isLeaf && !(data as unknown as Test).last_status && <UntestedStatus />}
            {node.props.isLeaf && (data as unknown as Test).last_status && (
              <Status
                id={(data as unknown as Test).last_status}
                name={(data as unknown as Test).last_status_name}
                color={(data as unknown as Test).last_status_color}
              />
            )}
          </td>
        )}
        {isVisible("id") && <td className={styles.containerItem}>{node.data.id}</td>}
        {isVisible("suite_path") && (
          <td className={styles.containerItem}>
            {node.props.isLeaf && (node.data as Test).suite_path}
          </td>
        )}
        {isVisible("assignee_username") && (
          <td className={styles.containerItem}>
            {node.props.isLeaf &&
              (!(data as unknown as Test).assignee_username ? (
                <span style={{ opacity: 0.7 }}>{t("Nobody")}</span>
              ) : (
                <div className={styles.avatarBlock}>
                  <UserAvatar size={32} avatar_link={(data as unknown as Test).avatar_link} />
                  <UserUsername username={(data as unknown as Test).assignee_username ?? ""} />
                </div>
              ))}
          </td>
        )}
        {isVisible("estimate") && (
          <td className={styles.containerItem}>{(node.data as Test).estimate ?? "-"}</td>
        )}
        {isVisible("labels") && (
          <td className={styles.containerItem}>
            <ul className={styles.list}>
              {node.props.isLeaf &&
                (data as unknown as Test).labels.map((label) => (
                  <li key={label.id}>
                    <Label content={label.name} color={colors.accent} />
                  </li>
                ))}
            </ul>
          </td>
        )}
        {isVisible("started_at") && (
          <td className={styles.containerItem}>
            {node.props.isLeaf ? "" : dayjs(data.started_at).format("YYYY-MM-DD HH:mm")}
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
