import { Flex, Form, Tree, Typography } from "antd"
import { useEffect, useState } from "react"
import { Control, Controller } from "react-hook-form"
import { useTranslation } from "react-i18next"

import { useTestCaseFormLabels } from "entities/label/model"

import { useTestCasesSearch } from "entities/test-case/model"

import { getTestCaseChangeResult } from "entities/test-plan/lib"

import { TestCaseLabels } from "features/test-plan/change-test-plan/ui/test-cases-form-item/ui/test-case-labels/test-case-labels"

import { TreeUtils } from "shared/libs"
import { ArchivedTag, ContainerLoader } from "shared/ui"

import { ChangeTestPlanForm, ErrorData } from "../../use-change-test-plan"
import styles from "./styles.module.css"
import { useTestCasesFilter } from "./use-test-cases-filter"

interface Props {
  errors: ErrorData | null
  control: Control<ChangeTestPlanForm>
}

export const TestCasesFormItem = ({ errors, control }: Props) => {
  const { t } = useTranslation()
  const [selectedLables, setSelectedLabels] = useState<number[]>([])
  const [lableCondition, setLableCondition] = useState<"and" | "or">("and")
  const [showArchived, setShowArchived] = useState(false)

  const handleConditionClick = () => {
    setLableCondition(lableCondition === "and" ? "or" : "and")
  }

  const handleToggleArchived = () => {
    setShowArchived(!showArchived)
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars, @typescript-eslint/no-explicit-any
  const setLables = (_: string, values: any, data: any) => {
    const v = values as { name: string; id?: number }[]
    setSelectedLabels(v.map((i) => i.id).filter((i) => i !== undefined))
  }

  const {
    searchText,
    treeData,
    expandedRowKeys,
    isLoading: isLoadingTreeData,
    onSearch,
    onRowExpand,
  } = useTestCasesSearch({ isShow: true })

  const labelProps = useTestCaseFormLabels({
    setValue: setLables,
    testCase: null,
    isShow: true,
    isEditMode: false,
    defaultLabels: selectedLables,
  })

  const { FilterButton, FilterForm } = useTestCasesFilter({
    labelProps,
    searchText,
    handleSearch: onSearch,
    selectedLables,
    lableCondition,
    handleConditionClick,
    showArchived,
    handleToggleArchived,
  })

  useEffect(() => {
    onSearch(searchText, selectedLables, lableCondition, showArchived)
  }, [selectedLables, lableCondition, showArchived])

  return (
    <Form.Item
      label={
        <div style={{ display: "flex", height: 22 }}>
          <Typography.Paragraph style={{ margin: 0 }}>{t("Test Cases")}</Typography.Paragraph>
          {FilterButton}
        </div>
      }
      validateStatus={errors?.test_cases ? "error" : ""}
      help={errors?.test_cases ? errors.test_cases : ""}
    >
      <Controller
        name="test_cases"
        control={control}
        render={({ field }) => {
          const testCases = field.value.filter((item: string) => !item.startsWith("TS"))
          return (
            <>
              {FilterForm}
              {isLoadingTreeData && <ContainerLoader />}
              {!isLoadingTreeData && (
                <>
                  <span
                    data-testid="create-test-plan-tree-selected"
                    style={{ display: "block", opacity: 0.7, marginBottom: 8 }}
                  >
                    {t("Selected")}: {testCases.length} {t("Test Cases").toLowerCase()}
                  </span>
                  <Tree
                    data-testid="create-test-plan-tree"
                    {...field}
                    //@ts-ignore
                    titleRender={(node: TestPlan) => {
                      return (
                        <>
                          <Flex data-testid={`test-case-title-${node.name}`} gap={6} align="center">
                            {node.is_archive && (
                              <ArchivedTag
                                data-testid={`test-case-archived-tag-${node.name}`}
                                size="sm"
                              />
                            )}
                            {node.title}
                          </Flex>
                          {node.labels ? <TestCaseLabels labels={node.labels} /> : null}
                        </>
                      )
                    }}
                    virtual={false}
                    showIcon
                    checkable
                    selectable={false}
                    //@ts-ignore
                    treeData={TreeUtils.deleteChildren<Suite>(treeData)}
                    checkedKeys={field.value}
                    onCheck={(checked, info) => {
                      // @ts-ignore
                      field.onChange(getTestCaseChangeResult(checked, info, field.value))
                    }}
                    expandedKeys={expandedRowKeys}
                    onExpand={(_, record) => {
                      onRowExpand(expandedRowKeys, String(record.node.key))
                    }}
                    className={styles.treeBlock}
                  />
                </>
              )}
            </>
          )
        }}
      />
    </Form.Item>
  )
}
