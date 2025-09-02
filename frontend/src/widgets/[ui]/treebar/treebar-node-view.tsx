import { Dropdown, Popover, Spin, Tooltip } from "antd"
import classNames from "classnames"
import { useTranslation } from "react-i18next"
import { Link, useSearchParams } from "react-router-dom"

import { TestSuitePopoverInfo } from "entities/suite/ui"

import { icons } from "shared/assets/inner-icons"
import { createConcatIdsFn } from "shared/libs"
import { LazyNodeProps, LazyTreeNodeApi, NodeId, TreeBaseLoadMore } from "shared/libs/tree"
import { ArchivedTag, HighLighterTesty } from "shared/ui"

import styles from "./styles.module.css"
import {
  TestPlanProps,
  TestSuiteProps,
  useTreebarNodeContextMenu,
} from "./use-treebar-node-context-menu"
import { saveUrlParamByKeys } from "./utils"

const { ArrowIcon, ExpandIcon, InfoIcon } = icons

interface Props {
  node: LazyTreeNodeApi<TestPlan | Suite, LazyNodeProps>
  projectId: number
  selectNodeId: string | null
  type: "plans" | "suites"
  searchText?: string
  onSelect: (nodeId: NodeId) => void
  onRoot: (nodeId: NodeId) => void
}

export const TreebarNodeView = ({
  node,
  projectId,
  selectNodeId,
  type,
  searchText,
  onSelect,
  onRoot,
}: Props) => {
  const { t } = useTranslation()

  const [searchParams] = useSearchParams()
  const offset = node.props.level * 20
  // @ts-ignore
  // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
  const nodeTitle = type === "plans" ? node.data.title : node.data.name

  const contextItems = useTreebarNodeContextMenu({
    type,
    data: node.data,
    projectId,
    tree: node.tree,
  } as TestPlanProps | TestSuiteProps)

  const handleSelect = () => {
    if (node.tree.selectedId === node.id) {
      node.tree.updateSelectId(null)
      return
    }
    node.tree.updateSelectId(node.id)
    onSelect(node.id)
  }

  const handleOpenClick = async () => {
    await node.open()
  }

  const handleMoreClick = async () => {
    await node.more()
  }

  const handleOpenContextMenu = (open: boolean) => {
    if (open) {
      node.select()
    } else {
      node.unselect()
    }
  }

  const IS_SELECTED_TREE_ID = String(selectNodeId) === String(node.id)
  const urlParams = saveUrlParamByKeys(["rootId", "ordering", "is_archive"], searchParams)

  if (localStorage.getItem("isDrawerRightFixed") && searchParams.get("test_case")) {
    urlParams.append("test_case", searchParams.get("test_case") ?? "")
  }

  const getIdWithTitle = createConcatIdsFn(nodeTitle as string)

  return (
    <>
      <div
        id={`${node.title}`}
        key={`${node.title}-${node.id}-treebar`}
        style={{ paddingLeft: offset }}
        data-testid={getIdWithTitle("treebar-node-view")}
      >
        <Dropdown
          menu={{ items: contextItems }}
          trigger={["contextMenu"]}
          onOpenChange={handleOpenContextMenu}
        >
          <div
            className={classNames(styles.nodeBody, {
              [styles.activeContextMenu]: node.props.isSelected,
              [styles.activeNode]: !!node.props.isSelected || IS_SELECTED_TREE_ID,
              [styles.noborder]: node.props.level === 0,
            })}
            onClick={(e) => {
              e.stopPropagation()
              handleSelect()
            }}
          >
            <div className={styles.nodeLeftAction}>
              {type === "plans" && (node.data as unknown as TestPlan).is_archive && (
                <ArchivedTag size="sm" data-testid={getIdWithTitle("treebar-archived-tag")} />
              )}
              {node.props.isLoading && <Spin size="small" className={styles.loader} />}
              {!node.props.isLoading && node.props.canOpen && (
                <ArrowIcon
                  width={16}
                  height={16}
                  className={classNames(styles.arrowIcon, {
                    [styles.arrowIconOpen]: node.props.isOpen,
                  })}
                  onClick={(e) => {
                    // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
                    e.stopPropagation()
                    handleOpenClick()
                  }}
                  data-testid={getIdWithTitle("treebar-arrow-icon")}
                />
              )}
            </div>
            <Link
              to={{
                pathname: `/projects/${projectId}/${type}/${node.id}`,
                search: urlParams.toString(),
              }}
              className={classNames(styles.treebarNodeLink, {
                [styles.activeLink]: node.props.isSelected ?? IS_SELECTED_TREE_ID,
              })}
              data-testid={getIdWithTitle("treebar-node-link")}
            >
              <HighLighterTesty
                searchWords={searchText ?? ""}
                textToHighlight={nodeTitle as string}
              />
            </Link>
            {type === "suites" && (
              <Popover
                content={
                  <TestSuitePopoverInfo
                    cases_count={(node.data as unknown as Suite).cases_count}
                    descendant_count={(node.data as unknown as Suite).descendant_count}
                    total_cases_count={(node.data as unknown as Suite).total_cases_count}
                    estimate={(node.data as unknown as Suite).estimates}
                  />
                }
                placement="right"
              >
                <InfoIcon
                  className={styles.infoIcon}
                  data-testid={getIdWithTitle("treebar-info-icon")}
                />
              </Popover>
            )}
            {node.props.canOpen && (
              <Tooltip title={t("Expand")} placement="right">
                <ExpandIcon
                  width={16}
                  height={16}
                  className={styles.expandIcon}
                  onClick={(e) => {
                    // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
                    e.stopPropagation()
                    onRoot(node.id)
                  }}
                  data-testid={getIdWithTitle("treebar-expand-button")}
                />
              </Tooltip>
            )}
          </div>
        </Dropdown>
      </div>
      {node.parent?.props.hasMore && node.isLast && (
        <TreeBaseLoadMore
          isLoading={node.parent.props.isLoading}
          node={node}
          onMore={handleMoreClick}
          isLast={false}
          isRoot={false}
        />
      )}
    </>
  )
}
