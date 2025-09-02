import { useEffect, useState } from "react"
import { useParams } from "react-router"

import { useLazySearchTestCasesQuery } from "entities/test-case/api"

import { TreeUtils, makeTestSuitesWithCasesForTreeView } from "shared/libs"

export const useTestCasesSearch = ({ isShow }: { isShow: boolean }) => {
  const { projectId } = useParams<ParamProjectId>()
  const [searchText, setSearchText] = useState("")
  const [treeData, setTreeData] = useState<DataWithKey<Suite>[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [searchTestCases] = useLazySearchTestCasesQuery()
  const [expandedRowKeys, setExpandedRowKeys] = useState<string[]>([])

  useEffect(() => {
    if (!isShow || !projectId) return
    const fetch = async () => {
      setIsLoading(true)
      const res = await searchTestCases({ project: projectId }).unwrap()
      const suitesWithKeys = makeTestSuitesWithCasesForTreeView(res)
      setTreeData(suitesWithKeys as unknown as DataWithKey<Suite>[])
      setIsLoading(false)
    }

    fetch()
  }, [isShow, projectId])

  const onSearch = async (
    value: string,
    labels: number[],
    labels_condition: LabelCondition,
    showArchived = false
  ) => {
    if (!projectId || !isShow) return
    if (value !== searchText) {
      setSearchText(value)
    }

    setIsLoading(true)
    const res = await searchTestCases({
      project: projectId,
      search: value,
      labels,
      labels_condition: labels.length > 1 ? labels_condition : undefined,
      is_archive: showArchived,
    }).unwrap()

    const suitesWithKeys = makeTestSuitesWithCasesForTreeView(res)

    const [filteredRows] = TreeUtils.filterRows(
      suitesWithKeys as unknown as DataWithKey<Suite>[],
      value,
      {
        isAllExpand: true,
        isShowChildren: true,
      }
    )

    if (!value.trim().length && !labels.length) {
      setExpandedRowKeys([])
    }
    setTreeData(filteredRows)
    setIsLoading(false)
  }

  const onRowExpand = (expandedRows: string[], recordKey: string) => {
    if (expandedRows.includes(recordKey)) {
      setExpandedRowKeys(expandedRows.filter((key) => key !== recordKey))
    } else {
      setExpandedRowKeys([...expandedRows, recordKey])
    }
  }

  const onClearSearch = () => {
    setSearchText("")
    setTreeData([])
    setExpandedRowKeys([])
  }

  return {
    searchText,
    treeData,
    expandedRowKeys,
    isLoading,
    onSearch,
    onRowExpand,
    onClearSearch,
  }
}
