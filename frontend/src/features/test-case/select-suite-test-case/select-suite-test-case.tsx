import { Button, Input, Modal } from "antd"
import Search from "antd/lib/input/Search"
import { makeNode } from "processes/treebar-provider/utils"
import { ChangeEvent, useContext, useEffect, useState } from "react"
import { useTranslation } from "react-i18next"

import { useLazyGetTestSuiteAncestorsQuery, useLazyGetTestSuitesQuery } from "entities/suite/api"

import { ProjectContext } from "pages/project"

import { config } from "shared/config"
import { useDebounce } from "shared/hooks"
import {
  LazyNodeProps,
  LazyTreeNodeApi,
  LazyTreeView,
  NodeId,
  TreeNodeFetcher,
} from "shared/libs/tree"

import styles from "./styles.module.css"
import { TreeNodeSuiteView } from "./tree-node-suite-view"

interface Props {
  suite: SelectData | null
  onChange: (suite: SelectData) => void
}

export const SelectSuiteTestCase = ({ suite, onChange }: Props) => {
  const { t } = useTranslation()
  const { project } = useContext(ProjectContext)!
  const [isSelectSuiteModalOpened, setIsSelectSuiteModalOpened] = useState(false)
  const [searchText, setSearchText] = useState("")
  const searchDebounce = useDebounce(searchText, 250, true)
  const [selectedSuite, setSelectedSuite] = useState<SelectData | null>(suite)

  const [getSuites] = useLazyGetTestSuitesQuery()
  const [getAncestors] = useLazyGetTestSuiteAncestorsQuery()

  const fetcher: TreeNodeFetcher<Suite, LazyNodeProps> = async (params) => {
    const res = await getSuites(
      {
        project: project.id,
        page: params.page,
        parent: params.parent ? Number(params.parent) : null,
        page_size: config.defaultTreePageSize,
        ordering: "name",
        treesearch: searchDebounce,
        _n: params._n,
      },
      true
    ).unwrap()

    const data = makeNode(res.results, params)
    return { data, nextInfo: res.pages, _n: params._n }
  }

  const fetcherAncestors = (id: NodeId) => {
    return getAncestors({ project: project.id, id: Number(id) }).unwrap()
  }

  const handleSearch = (e: ChangeEvent<HTMLInputElement>) => {
    setSearchText(e.target.value)
  }

  const handleSelect = (node: LazyTreeNodeApi<Suite, LazyNodeProps> | null) => {
    if (node) {
      setSelectedSuite({ value: node.data.id, label: node.data.name })
    }
  }

  const handleSelectApply = () => {
    if (selectedSuite) {
      onChange(selectedSuite)
      setIsSelectSuiteModalOpened(false)
    }
  }

  useEffect(() => {
    setSelectedSuite(suite)
  }, [suite])

  return (
    <>
      <div style={{ display: "flex", alignItems: "center" }}>
        <Input
          id="suite-edit-input"
          value={suite?.label?.toString()}
          readOnly
          style={{ width: "100%" }}
          onClick={() => setIsSelectSuiteModalOpened(true)}
        />
      </div>
      <Modal
        title={t("Select suite")}
        open={isSelectSuiteModalOpened}
        onCancel={() => setIsSelectSuiteModalOpened(false)}
        width="700px"
        className="select-suite-modal"
        footer={[
          <Button id="close-btn" key="back" onClick={() => setIsSelectSuiteModalOpened(false)}>
            {t("Close")}
          </Button>,
          <Button id="select-suite" key="submit" type="primary" onClick={handleSelectApply}>
            {t("Select")}
          </Button>,
        ]}
      >
        <Search style={{ marginBottom: 8 }} placeholder={t("Search")} onChange={handleSearch} />
        <div className={styles.treeBlock}>
          <LazyTreeView
            // @ts-ignore
            fetcher={fetcher}
            fetcherAncestors={fetcherAncestors}
            initDependencies={[searchDebounce, isSelectSuiteModalOpened]}
            selectedId={selectedSuite?.value}
            renderNode={(node) => (
              <TreeNodeSuiteView
                node={node as LazyTreeNodeApi<Suite, LazyNodeProps>} // FIX IT cast type
                selectedId={selectedSuite?.value}
                onSelect={handleSelect}
              />
            )}
          />
        </div>
      </Modal>
    </>
  )
}
