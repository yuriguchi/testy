import Search from "antd/es/input/Search"
import { makeNode } from "processes/treebar-provider/utils"
import { ChangeEvent, useContext, useEffect, useRef, useState } from "react"

import { LazyGetTriggerType } from "app/export-types"

import { ProjectContext } from "pages/project"

import { config } from "shared/config"
import { useDebounce, useOnClickOutside } from "shared/hooks"
import {
  LazyNodeProps,
  LazyTreeNodeApi,
  LazyTreeView,
  NodeId,
  TreeNodeFetcher,
} from "shared/libs/tree"

import { LazyTreeSearchNode } from "./lazy-tree-search-node"
import styles from "./styles.module.css"

export interface BaseSearchEntity {
  id: number
  name: string
  has_children: boolean
}

interface Props<T> {
  id: string
  getData: LazyGetTriggerType<T>
  getAncestors: LazyGetTriggerType<T>
  onSelect: (node: LazyTreeNodeApi<unknown, LazyNodeProps> | null) => void
  projectId: string
  searchValue?: string
  skipInit?: boolean
  selectedId?: NodeId | null
  placeholder?: string
  valueKey?: string
  disabled?: boolean
  dataParams?: Record<string, unknown>
}

export const LazyTreeSearch = <T extends BaseSearchEntity>({
  id,
  getData,
  getAncestors,
  onSelect,
  selectedId,
  skipInit = true,
  placeholder,
  valueKey = "name",
  disabled = false,
  searchValue = "",
  dataParams,
}: Props<T>) => {
  const { project } = useContext(ProjectContext)!
  const [searchInputText, setSearchInputText] = useState(searchValue)
  const [searchText, setSearchText] = useState(searchValue)
  const [isShowDropdown, setIsShowDropdown] = useState(false)
  const searchDebounce = useDebounce(searchText, 250, true)
  const popupRef = useRef(null)

  const handleDropdownClickOutside = () => {
    setIsShowDropdown(false)
    setSearchText(selectedId ? searchValue : "")
    setSearchInputText(selectedId ? searchValue : "")
  }

  useOnClickOutside(popupRef, handleDropdownClickOutside, true, [`#${id}`])

  const fetcher: TreeNodeFetcher<unknown, LazyNodeProps> = async (params) => {
    const res = await getData(
      {
        project: project.id,
        page: params.page,
        parent: params.parent ? Number(params.parent) : null,
        page_size: config.defaultTreePageSize,
        ordering: "name",
        treesearch: searchDebounce,
        _n: params._n,
        ...dataParams,
      },
      true
    ).unwrap()

    // @ts-ignore
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const data = makeNode(res.results, (item) => ({ ...params, title: item[valueKey] }))
    return { data, nextInfo: res.pages, _n: params._n }
  }

  const fetcherAncestors = async (newId: NodeId): Promise<number[]> => {
    return (await getAncestors({
      project: project.id,
      id: Number(newId),
    }).unwrap()) as unknown as Promise<number[]>
  }

  const handleSearch = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value

    setSearchText(value)
    setSearchInputText(value)

    if (!value.length) {
      onSelect(null)
    }
  }

  const handleSearchClick = () => {
    setIsShowDropdown(true)
  }

  const handleSelect = (node: LazyTreeNodeApi<unknown, LazyNodeProps> | null) => {
    if (node) {
      setSearchInputText(node.title)
      onSelect(node)
      setIsShowDropdown(false)
    }
  }

  useEffect(() => {
    setSearchInputText(searchValue)
  }, [searchValue])

  return (
    <div className={styles.searchContainer}>
      <Search
        id={id}
        style={{ marginBottom: 8 }}
        placeholder={placeholder}
        onChange={handleSearch}
        onClick={handleSearchClick}
        value={searchInputText}
        allowClear
        disabled={disabled}
      />
      {isShowDropdown && !disabled && (
        <div className={styles.searchDropdown} ref={popupRef} data-testid={`${id}-search-dropdown`}>
          <LazyTreeView
            fetcher={fetcher}
            fetcherAncestors={fetcherAncestors}
            skipInit={skipInit}
            selectedId={selectedId}
            initDependencies={[searchDebounce]}
            renderNode={(node) => (
              <LazyTreeSearchNode
                node={node}
                selectedId={selectedId}
                onSelect={handleSelect}
                searchText={searchInputText}
              />
            )}
          />
        </div>
      )}
    </div>
  )
}
