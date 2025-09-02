import { Checkbox, Form, Select } from "antd"
import Search from "antd/es/input/Search"
import { useStatuses } from "entities/status/model/use-statuses"
import { makeNode } from "processes/treebar-provider/utils"
import { ChangeEvent, useContext, useState } from "react"
import { useTranslation } from "react-i18next"

import { useLazyGetTestSuitesQuery } from "entities/suite/api"

import { ProjectContext } from "pages/project"

import { config } from "shared/config"
import { useDebounce } from "shared/hooks"
import { LazyNodeProps, LazyTreeNodeApi, LazyTreeView, TreeNodeFetcher } from "shared/libs/tree"
import { Status } from "shared/ui"

import { SelectSuitesNode } from "../../select-suites-node/select-suites-node"
import styles from "./styles.module.css"

interface Props {
  value: CustomAttributeAppliedToUpdate
  onChange: (value: CustomAttributeAppliedToUpdate) => void
}

export const TestResultTypeForm = ({ value, onChange }: Props) => {
  const { t } = useTranslation()
  const { project } = useContext(ProjectContext)!
  const [searchText, setSearchText] = useState("")
  const searchDebounce = useDebounce(searchText, 250, true)

  const [getSuites] = useLazyGetTestSuitesQuery()

  const { statuses } = useStatuses({ project: project.id })

  const handleSearchChange = (e: ChangeEvent<HTMLInputElement>) => {
    setSearchText(e.target.value)
  }

  const handleStatusChange = (selectValue: number[]) => {
    onChange({ ...value, testresult: { ...value.testresult, status_specific: selectValue } })
  }

  const handleRequiredChange = () => {
    onChange({
      ...value,
      testresult: { ...value.testresult, is_required: !value.testresult.is_required },
    })
  }

  const handleSuiteSpecificChange = () => {
    const isSuiteSpecific = !value.testresult.is_suite_specific
    onChange({
      ...value,
      testresult: {
        ...value.testresult,
        is_suite_specific: isSuiteSpecific,
        suite_ids: !isSuiteSpecific ? [] : value.testresult.suite_ids,
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
      isChecked: value.testresult.suite_ids.includes(item.id) ?? false,
    }))
    return { data, nextInfo: res.pages, _n: params._n }
  }

  const handleCheckSuite = (suiteId: number) => {
    onChange({
      ...value,
      testresult: {
        ...value.testresult,
        suite_ids: value.testresult.suite_ids?.includes(suiteId)
          ? value.testresult.suite_ids?.filter((i) => i !== suiteId)
          : [...(value.testresult.suite_ids ?? []), suiteId],
      },
    })
  }

  return (
    <div className={styles.wrapper}>
      <Form.Item label={t("Result Status")} style={{ marginBottom: 0 }}>
        <Select
          id="select-status"
          placeholder={t("Please select")}
          mode="multiple"
          allowClear
          showSearch={false}
          value={value.testresult.status_specific}
          onChange={handleStatusChange}
          className={styles.selectStatus}
        >
          {statuses.map((status) => (
            <Select.Option key={status.id} value={status.id}>
              <Status id={status.id} name={status.name} color={status.color} />
            </Select.Option>
          ))}
        </Select>
      </Form.Item>
      <Checkbox
        data-testid="checkbox-is-required"
        className="checkbox-md"
        checked={value.testresult.is_required}
        onChange={handleRequiredChange}
      >
        {t("Required")}
      </Checkbox>
      <Checkbox
        data-testid="checkbox-suite-specific"
        className="checkbox-md"
        checked={value.testresult.is_suite_specific}
        onChange={handleSuiteSpecificChange}
      >
        {t("Suite specific")}
      </Checkbox>
      {value.testresult.is_suite_specific && (
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
