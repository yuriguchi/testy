import { Button, Divider, Flex, Tooltip, Typography } from "antd"
import { memo, useContext } from "react"
import { useTranslation } from "react-i18next"

import { useAppDispatch, useAppSelector } from "app/hooks"

import {
  clearFilter,
  selectFilterCount,
  selectSettings,
  updateFilterSettings,
  updateSettings,
} from "entities/test-case/model"

import { ClearFilters } from "features/filter"
import { CreateTestCase } from "features/test-case"

import CollapseIcon from "shared/assets/icons/arrows-in-simple.svg?react"
import { saveVisibleColumns } from "shared/libs"
import { DataViewSelect } from "shared/ui"

import { SettingsColumnVisibility } from "widgets/settings-column-visibility/settings-column-visibility"
import {
  TestCasesButtonFilterDrawer,
  TestCasesSavedFilters,
  TestCasesSorter,
  TestCasesTreeContext,
} from "widgets/test-case"

interface Props {
  dataView: "list" | "tree"
  setDataView: (dataView: "list" | "tree") => void
  suite?: Suite
}

export const TestSuiteDataActions = memo(({ dataView, setDataView, suite }: Props) => {
  const { t } = useTranslation()
  const { testCasesTree } = useContext(TestCasesTreeContext)!

  const dispatch = useAppDispatch()
  const tableSettings = useAppSelector(selectSettings<TestTableParams>("table"))
  const treeSettings = useAppSelector(selectSettings<TestTreeParams>("tree"))
  const testCasesSelectedCount = useAppSelector(selectFilterCount)

  const isList = dataView === "list"
  const visibleColumns = isList ? tableSettings.visibleColumns : treeSettings.visibleColumns
  const columns = isList ? tableSettings.columns : treeSettings.columns

  const handleChangeVisibleColumns = (newVisibleColumns: ColumnParam[]) => {
    const key = isList ? "table" : "tree"
    dispatch(
      updateSettings({
        key,
        settings: {
          visibleColumns: newVisibleColumns,
        },
      })
    )
    saveVisibleColumns(`test-cases-visible-cols-${key}`, newVisibleColumns)
  }

  const handleClearFilter = () => {
    dispatch(updateFilterSettings({ selected: null }))
    dispatch(clearFilter())
  }

  return (
    <Flex justify="space-between" align="center" style={{ width: "100%", marginBottom: 24 }}>
      <Flex gap={16} wrap>
        <Typography.Title
          level={2}
          style={{ marginBottom: 0, alignSelf: "center", textWrap: "nowrap" }}
        >
          {t("Test Cases")}
        </Typography.Title>
        {!!suite && <CreateTestCase />}
      </Flex>
      <Flex gap={8} wrap justify="flex-end" align="center">
        <Flex gap={8} align="center">
          <ClearFilters isVisible={!!testCasesSelectedCount} onClear={handleClearFilter} />
          <TestCasesButtonFilterDrawer />
          <TestCasesSavedFilters />
          <TestCasesSorter />
        </Flex>
        {!isList && (
          <Tooltip title={t("Collapse All")}>
            <Button
              icon={<CollapseIcon width={18} height={18} color="var(--y-sky-60)" />}
              onClick={() => testCasesTree.current?.closeAll()}
              data-testid="test-cases-collapse-all-btn"
            />
          </Tooltip>
        )}
        <SettingsColumnVisibility
          id={
            isList ? "test-cases-table-setting-columns-btn" : "test-cases-tree-setting-columns-btn"
          }
          columns={columns}
          visibilityColumns={visibleColumns}
          onChange={handleChangeVisibleColumns}
        />
        <Divider type="vertical" style={{ height: "1.5em" }} />
        <DataViewSelect value={dataView} onChange={setDataView} />
      </Flex>
    </Flex>
  )
})

TestSuiteDataActions.displayName = "TestSuiteDataActions"
