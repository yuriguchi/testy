import { SearchOutlined } from "@ant-design/icons"
import { Button, Flex, Input, Select, Tree, TreeDataNode } from "antd"
import { DataNode } from "antd/es/tree"
import { TreeProps } from "antd/lib"
import React, { Key, useEffect, useMemo, useState } from "react"
import { useTranslation } from "react-i18next"

import { ContainerLoader, Toggle } from "shared/ui"

import styles from "./styles.module.css"
import { BaseTreeFilterNode, treeFilterFormat } from "./utils"

interface TreeDataNodeExtend extends TreeDataNode {
  titleText: string
  children: TreeDataNodeExtend[]
}

interface Props<T> {
  type: "suites" | "plans"
  getData: () => Promise<T[]>
  getDataFromRoot: () => Promise<T[]>
  value: number[]
  onChange: (keys: number[]) => void
  onClose?: () => void
  onClear?: () => void
}

function findNodesWithParentKeys(
  tree: TreeDataNodeExtend[],
  title: string,
  parentKey: Key | null = null,
  path: Key[] = []
): Key[] {
  let results: Key[] = []

  for (const node of tree) {
    const currentPath = [...path, parentKey].filter(Boolean) as Key[]

    if (String(node.titleText.toLowerCase()).includes(title.toLowerCase())) {
      results.push(...currentPath)
    }

    if (node.children && node.children.length > 0) {
      results = results.concat(findNodesWithParentKeys(node.children, title, node.key, currentPath))
    }
  }

  return Array.from(new Set(results))
}

function findTreeNodeById<T extends BaseTreeFilterNode>(
  tree: T[],
  id: number
): BaseTreeFilterNode | null {
  for (const node of tree) {
    if (Number(node.id) === id) {
      return node
    }
    if (node.children) {
      const found = findTreeNodeById(node.children, id)
      if (found) {
        return found
      }
    }
  }
  return null
}

const getAllParentIdsByNode = (
  allNodes: BaseTreeFilterNode[],
  node: BaseTreeFilterNode,
  parentIds: number[] = []
) => {
  if (node?.parent?.id) {
    parentIds.push(node.parent.id)
    const parentNode = findTreeNodeById(allNodes, node.parent.id)
    if (parentNode) {
      return getAllParentIdsByNode(allNodes, parentNode, parentIds)
    }
  }
  return parentIds
}

export const EntityTreeFilter = <T extends BaseTreeFilterNode>({
  type,
  value,
  getData,
  getDataFromRoot,
  onChange,
  onClose,
  onClear,
}: Props<T>) => {
  const { t } = useTranslation()

  const [isOpen, setIsOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [isShowFullTree, setIsShowFullTree] = useState(false)
  const [halfChecked, setHalfChecked] = useState<string[]>([])
  const [expandedKeys, setExpandedKeys] = useState<Key[]>([])
  const [autoExpandParent, setAutoExpandParent] = useState(true)
  const [searchValue, setSearchValue] = useState("")
  const [allEntityData, setAllEntityData] = useState<T[]>([])
  const [visibleShortData, setVisibleShortData] = useState<T[]>([])

  const visibleData = isShowFullTree ? allEntityData : visibleShortData

  const treeData = useMemo(() => {
    if (!visibleData.length) {
      return { data: [], selectedData: [] }
    }

    const [data, selectedData] = treeFilterFormat<T>({
      data: visibleData,
      searchValue,
      titleKey: type === "plans" ? "title" : "name",
    })
    return {
      data,
      selectedData,
    }
  }, [visibleData, searchValue])

  useEffect(() => {
    const prepareHalfCheked = (nodes: BaseTreeFilterNode[], checked: number[] = []) => {
      for (const node of nodes) {
        if (checkedKeys.includes(String(node.id))) {
          // @ts-ignore
          // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
          if (node?.parent?.id) {
            checked.push(...getAllParentIdsByNode(visibleData, node))
          }
        }

        if (node.children.length) {
          prepareHalfCheked(node.children, checked)
        }
      }

      return checked
    }

    setHalfChecked([...new Set(prepareHalfCheked(visibleData).map((i) => String(i)))])
  }, [visibleData, value])

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value: newValue } = e.target

    // eslint-disable-next-line @typescript-eslint/no-unsafe-argument
    const newExpandedKeys = findNodesWithParentKeys(treeData.data, newValue)
    setExpandedKeys(newExpandedKeys)
    setSearchValue(newValue)
    setAutoExpandParent(true)
  }

  const handleExpand = (newExpandedKeys: React.Key[]) => {
    setExpandedKeys(newExpandedKeys)
    setAutoExpandParent(false)
  }

  const handleSelectAll = () => {
    onChange(treeData.selectedData)
  }

  const handleDropdownVisibleChange = (toggle: boolean) => {
    setIsOpen(toggle)
    if (!toggle) {
      setSearchValue("")
      onClose?.()
    }
  }

  const handleChange = (
    dataValue: {
      value: string
      label: string | undefined
    }[]
  ) => {
    const keys = dataValue.map((i) => Number(i.value))
    if (!keys.length) {
      onClear?.()
      return
    }

    onChange(keys)
  }

  const handleCheck: TreeProps["onCheck"] = (checkedKeysValue, info) => {
    const { node, checked } = info
    let newCheckedKeys = [...checkedKeys]

    if (checked) {
      const addKeys = (addedNode: DataNode) => {
        if (!newCheckedKeys.includes(addedNode.key as string)) {
          newCheckedKeys.push(addedNode.key as string)
        }
        addedNode.children?.forEach(addKeys)
      }
      addKeys(node)
    } else {
      const removeKeys = (removedNode: DataNode) => {
        newCheckedKeys = newCheckedKeys.filter((key) => key !== removedNode.key)
        removedNode.children?.forEach(removeKeys)
      }
      removeKeys(node)
    }

    onChange(newCheckedKeys.map(Number))
  }

  const handleShowFullTree = (toggle: boolean) => {
    setIsShowFullTree(toggle)
  }

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true)
      const allData = await getDataFromRoot()
      const shortData = await getData()
      setAllEntityData(allData)
      setVisibleShortData(shortData)
      setIsLoading(false)
    }

    fetchData()
  }, [])

  const checkedKeys = value.map(String)

  const checkedKeysWithLabel = useMemo(() => {
    return value.map((val) => {
      const node = findTreeNodeById(allEntityData, val)
      return {
        value: String(val),
        label: node ? (type === "plans" ? node.title : node.name) : String(val),
      }
    })
  }, [value, allEntityData, type])

  const PLACEHOLDER_SELECT =
    type === "plans" ? t("Filter by Test Plans") : t("Filter by Test Suites")

  return (
    <Select
      id={`${type}-tree-filter`}
      value={isLoading ? [] : checkedKeysWithLabel}
      labelInValue
      mode="multiple"
      maxTagCount={6}
      showSearch={false}
      placeholder={PLACEHOLDER_SELECT}
      defaultActiveFirstOption={false}
      filterOption={false}
      open={isOpen}
      loading={isLoading}
      onClear={onClear}
      onChange={handleChange}
      allowClear
      style={{ width: "100%" }}
      dropdownStyle={{ padding: 0 }}
      onDropdownVisibleChange={handleDropdownVisibleChange}
      dropdownRender={() => (
        <>
          <div className={styles.searchBlock} data-testid="entity-tree-filter-search-block">
            <Input
              className={styles.input}
              placeholder={t("Search")}
              variant="borderless"
              value={searchValue}
              autoFocus
              onChange={handleSearch}
              suffix={<SearchOutlined style={{ color: "rgba(0,0,0,.45)" }} />}
            />
          </div>
          <div style={{ padding: "8px 16px" }}>
            <Flex align="center" justify="space-between" style={{ marginBottom: 8 }}>
              <Flex gap={8}>
                <Button
                  size="small"
                  onClick={handleSelectAll}
                  style={{ padding: "4px 8px" }}
                  data-testid="entity-tree-filter-select-all"
                >
                  {t("Select all")}
                </Button>
                <Button
                  onClick={onClear}
                  size="small"
                  style={{ padding: "4px 8px" }}
                  data-testid="entity-tree-filter-reset"
                >
                  {t("Reset")}
                </Button>
              </Flex>
              <Toggle
                id={`${type}-toggle-show-full-tree`}
                label={t("Show full tree")}
                labelFontSize={14}
                checked={isShowFullTree}
                onChange={handleShowFullTree}
                size="sm"
              />
            </Flex>
            {isLoading && <ContainerLoader />}
            {!isLoading && (
              <>
                <Tree
                  checkable
                  checkStrictly
                  defaultCheckedKeys={checkedKeys}
                  height={300}
                  virtual={false}
                  showIcon={false}
                  selectable={false}
                  treeData={treeData.data}
                  autoExpandParent={autoExpandParent}
                  onExpand={handleExpand}
                  expandedKeys={expandedKeys}
                  checkedKeys={{ checked: checkedKeys, halfChecked }}
                  onCheck={handleCheck}
                  className={styles.tree}
                  data-testid="entity-tree-filter-tree"
                />

                <span
                  style={{ opacity: 0.7, marginTop: 4 }}
                  data-testid="entity-tree-filter-selected-count"
                >
                  {t("Selected")}: {value.length}
                </span>
              </>
            )}
          </div>
        </>
      )}
    />
  )
}
