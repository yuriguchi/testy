import { Checkbox } from "antd"
import Search from "antd/es/input/Search"
import { makeNode } from "processes/treebar-provider/utils"
import { ChangeEvent, useContext, useState } from "react"
import { useTranslation } from "react-i18next"

import { useLazyGetTestSuitesQuery } from "entities/suite/api"

import { ProjectContext } from "pages/project"

import { config } from "shared/config"
import { useDebounce } from "shared/hooks"
import { LazyNodeProps, LazyTreeNodeApi, LazyTreeView, TreeNodeFetcher } from "shared/libs/tree"

import { SelectSuitesNode } from "../../select-suites-node/select-suites-node"
import styles from "./styles.module.css"

interface Props {
  value: CustomAttributeAppliedToUpdate
  onChange: (value: CustomAttributeAppliedToUpdate) => void
}

export const TestCaseTypeForm = ({ value, onChange }: Props) => {
  const { t } = useTranslation()
  const { project } = useContext(ProjectContext)!
  const [searchText, setSearchText] = useState("")
  const searchDebounce = useDebounce(searchText, 250, true)

  const [getSuites] = useLazyGetTestSuitesQuery()

  const handleSearchChange = (e: ChangeEvent<HTMLInputElement>) => {
    setSearchText(e.target.value)
  }

  const handleRequiredChange = () => {
    onChange({
      ...value,
      testcase: { ...value.testcase, is_required: !value.testcase.is_required },
    })
  }

  const handleSuiteSpecificChange = () => {
    const isSuiteSpecific = !value.testcase.is_suite_specific
    onChange({
      ...value,
      testcase: {
        ...value.testcase,
        is_suite_specific: isSuiteSpecific,
        suite_ids: !isSuiteSpecific ? [] : value.testcase.suite_ids,
      },
    })
  }

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

    const data = makeNode(res.results, params, (item) => ({
      isChecked: value.testcase.suite_ids.includes(item.id) ?? false,
    }))
    return { data, nextInfo: res.pages, _n: params._n }
  }

  const handleCheckSuite = (suiteId: number) => {
    onChange({
      ...value,
      testcase: {
        ...value.testcase,
        suite_ids: value.testcase.suite_ids?.includes(suiteId)
          ? value.testcase.suite_ids?.filter((i) => i !== suiteId)
          : [...(value.testcase.suite_ids ?? []), suiteId],
      },
    })
  }

  return (
    <div className={styles.wrapper}>
      <Checkbox
        data-testid="checkbox-is-required"
        className="checkbox-md"
        checked={value.testcase.is_required}
        onChange={handleRequiredChange}
      >
        {t("Required")}
      </Checkbox>
      <Checkbox
        data-testid="checkbox-suite-specific"
        className="checkbox-md"
        checked={value.testcase.is_suite_specific}
        onChange={handleSuiteSpecificChange}
      >
        {t("Suite specific")}
      </Checkbox>
      {value.testcase.is_suite_specific && (
        <div className={styles.suiteSpecificBlock}>
          <Search
            data-testid="search-input"
            placeholder="Search"
            onChange={handleSearchChange}
            value={searchText}
            style={{ marginBottom: "8px" }}
          />
          <div className={styles.treeBlock}>
            <LazyTreeView
              fetcher={fetcher}
              initDependencies={[searchDebounce]}
              renderNode={(node) => (
                <SelectSuitesNode
                  node={node as LazyTreeNodeApi<Suite, LazyNodeProps>} // FIX IT cast type
                  onCheck={handleCheckSuite}
                  searchText={searchText}
                />
              )}
            />
          </div>
        </div>
      )}
    </div>
  )
}
