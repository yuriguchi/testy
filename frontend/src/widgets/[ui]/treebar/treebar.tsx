import { Button, Flex, Input, Popover, Tooltip, Typography } from "antd"
import classNames from "classnames"
import { TreebarContext } from "processes"
import { ChangeEvent, useContext, useRef } from "react"
import { useTranslation } from "react-i18next"
import { useNavigate, useParams, useSearchParams } from "react-router-dom"

import { ChangeTestSuite } from "features/suite"
import { ChangeTestPlan } from "features/test-plan"

import { ProjectContext } from "pages/project/project-layout"

import CollapseIcon from "shared/assets/icons/arrows-in-simple.svg?react"
import { icons } from "shared/assets/inner-icons"
import { useResizebleBlock } from "shared/hooks"
import { LazyTreeView } from "shared/libs/tree"
import { LazyNodeProps, LazyTreeNodeApi, NodeId } from "shared/libs/tree/api"
import { ArchivedTag, ResizeLine } from "shared/ui"

import styles from "./styles.module.css"
import { TreebarBreadcrumbs } from "./treebar-breadcrumbs"
import { TreebarFilter } from "./treebar-filter"
import { TreebarNodeView } from "./treebar-node-view"
import { saveUrlParamByKeys } from "./utils"

const { BackIcon, FilterIcon } = icons

const MIN_WITH_TREE = 72
const DEFAULT_WITH_TREE = 374
const MAX_WITH_TREE_PERCENT = 70
const MAX_SMALLEST_SIZE = 172

export const Treebar = () => {
  const { t } = useTranslation()
  const { project } = useContext(ProjectContext)!
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const { testSuiteId, testPlanId } = useParams<ParamTestSuiteId & ParamTestPlanId>()

  const {
    treebar,
    searchText,
    treeSettings,
    fetcher,
    fetcherAncestors,
    initParent,
    selectedId,
    initDependencies,
    skipInit,
    activeTab,
    updateTreeSettings,
    setSearchText,
  } = useContext(TreebarContext)!

  const TREE_TITLES = {
    suites: t("Test Suites & Cases"),
    plans: t("Test Plans & Results"),
  }

  const wrapperRef = useRef<HTMLDivElement>(null)
  const { width, handleMouseDown, setWidth } = useResizebleBlock({
    key: "treebar",
    elRef: wrapperRef,
    defaultWidth: treeSettings.collapsed ? MIN_WITH_TREE : DEFAULT_WITH_TREE,
    minWidth: MIN_WITH_TREE,
    maxWidth: MAX_WITH_TREE_PERCENT,
    maxAsPercent: true,
    updater: (newWidth: number) => {
      updateTreeSettings({ collapsed: newWidth < 200 })
    },
  })

  const selectNodeId = testPlanId ?? testSuiteId ?? null

  const handleCollapsedTreeBar = () => {
    updateTreeSettings({ collapsed: !treeSettings.collapsed })
    setWidth(!treeSettings.collapsed ? MIN_WITH_TREE : DEFAULT_WITH_TREE)
  }

  const handleSearch = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setSearchText(value)
    if (value.length) {
      const urlParams = Object.fromEntries([...searchParams])
      setSearchParams({ ...urlParams, treeSearch: value })
    } else {
      searchParams.delete("treeSearch")
      setSearchParams(searchParams)
    }
  }

  const handleSelectNode = (nodeId: NodeId) => {
    const urlParams = saveUrlParamByKeys(["rootId", "ordering", "is_archive"], searchParams)

    if (localStorage.getItem("isDrawerRightFixed") && searchParams.get("test_case")) {
      urlParams.append("test_case", searchParams.get("test_case") ?? "")
    }

    navigate({
      pathname: `/projects/${project.id}/${activeTab}/${nodeId}`,
      search: urlParams.toString(),
    })
  }

  const handleRootNode = (nodeId: NodeId) => {
    const urlParams = { ...Object.fromEntries([...searchParams]), rootId: String(nodeId) }
    const queryParams = new URLSearchParams(urlParams)
    navigate({
      pathname: `/projects/${project.id}/${activeTab}/${nodeId}`,
      search: queryParams.toString(),
    })
  }

  const handleCloseAll = () => {
    treebar.current?.closeAll()
  }

  const IS_MINIFY = width < MAX_SMALLEST_SIZE || treeSettings.collapsed

  return (
    <div
      className={classNames(styles.wrapper, { [styles.collapsed]: treeSettings.collapsed })}
      ref={wrapperRef}
      style={{ width: treeSettings.collapsed ? MIN_WITH_TREE : width }}
    >
      <div className={styles.container}>
        <div className={styles.topBlock}>
          <div className={styles.header}>
            <div
              className={classNames(styles.headerBlock, {
                [styles.headerBlockMin]: IS_MINIFY,
              })}
            >
              <Flex gap={8}>
                {project.is_archive && <ArchivedTag size="lg" />}
                <Typography.Title level={1} className={styles.headerTitle}>
                  {project.name}
                </Typography.Title>
              </Flex>
              <div className={styles.backBlock}>
                <button
                  className={styles.backBtn}
                  type="button"
                  onClick={handleCollapsedTreeBar}
                  data-testid="treebar-back-button"
                >
                  <BackIcon width={24} height={24} />
                </button>
              </div>
            </div>
            <span className={styles.activeTab}>{activeTab ? TREE_TITLES[activeTab] : ""}</span>
            {!IS_MINIFY && (
              <TreebarBreadcrumbs activeTab={activeTab} entityId={testSuiteId ?? testPlanId} />
            )}
            <div
              className={classNames(styles.actionBlock, {
                [styles.actionBlockMin]: IS_MINIFY,
              })}
            >
              {activeTab === "suites" ? (
                <ChangeTestSuite
                  type="create"
                  size={IS_MINIFY ? "small" : "default"}
                  colorType="primary"
                />
              ) : (
                <ChangeTestPlan
                  type="create"
                  size={IS_MINIFY ? "small" : "default"}
                  colorType="primary"
                />
              )}
            </div>
          </div>
          <div className={styles.searchBlock}>
            <div className={styles.searchInputWrapper} data-testid="treebar-search-input-wrapper">
              <Input.Search
                placeholder={t("Search")}
                value={searchText}
                onChange={handleSearch}
                data-testid="treebar-search-input"
              />
            </div>
            {!IS_MINIFY && activeTab && (
              <Tooltip title={t("Filter & sort")}>
                <Popover
                  content={<TreebarFilter activeTab={activeTab} />}
                  arrow={false}
                  trigger="click"
                  placement="bottom"
                >
                  <Button
                    style={{ minWidth: 32 }}
                    icon={<FilterIcon width={24} height={24} color="var(--y-sky-60)" />}
                    data-testid="treebar-filter-button"
                  />
                </Popover>
              </Tooltip>
            )}
            <Tooltip title={t("Collapse All")}>
              <Button
                style={{ minWidth: 32 }}
                icon={<CollapseIcon width={18} height={18} color="var(--y-sky-60)" />}
                onClick={handleCloseAll}
                data-testid="treebar-collapse-all-button"
              />
            </Tooltip>
          </div>
        </div>
        {activeTab && !treeSettings.collapsed && (
          <div className={styles.treeViewBlock} data-testid={`tree-view-${activeTab}`}>
            <LazyTreeView
              // @ts-ignore // TODO fix forward ref type
              ref={treebar}
              cacheKey={`${project.id}-treebar-${activeTab}`}
              fetcher={fetcher}
              fetcherAncestors={fetcherAncestors}
              skipInit={skipInit || treeSettings.collapsed}
              initParent={initParent}
              selectedId={selectedId}
              initDependencies={initDependencies}
              renderNode={(node) => (
                <TreebarNodeView
                  projectId={project.id}
                  selectNodeId={selectNodeId}
                  type={activeTab}
                  searchText={searchText}
                  node={node as LazyTreeNodeApi<TestPlan | Suite, LazyNodeProps>} // FIX IT cast type
                  onSelect={handleSelectNode}
                  onRoot={handleRootNode}
                />
              )}
            />
          </div>
        )}
      </div>
      {!IS_MINIFY && <ResizeLine onMouseDown={handleMouseDown} />}
    </div>
  )
}
