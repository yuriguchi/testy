import { Button, Divider, Flex, Tooltip, Typography } from "antd"
import { memo, useContext } from "react"
import { useTranslation } from "react-i18next"
import { SettingsColumnVisibility } from "widgets"

import { useAppDispatch, useAppSelector } from "app/hooks"

import { useBulkUpdateMutation } from "entities/test/api"
import {
  clearFilter,
  selectFilter,
  selectFilterCount,
  selectSettings,
  updateFilterSettings,
  updateSettings,
} from "entities/test/model"

import { ClearFilters } from "features/filter"
import { MoveTests } from "features/test-plan"
import { AssignTestsBulk } from "features/test-result"

import CollapseIcon from "shared/assets/icons/arrows-in-simple.svg?react"
import { saveVisibleColumns } from "shared/libs"
import { DataViewSelect } from "shared/ui"

import {
  TestsButtonFilterDrawer,
  TestsSavedFilters,
  TestsSorter,
  TestsTreeContext,
} from "widgets/tests"

interface Props {
  testPlanId?: number
  dataView: "tree" | "list"
  setDataView: (dataView: "tree" | "list") => void
}

export const TestPlanDataActions = memo(({ testPlanId, dataView, setDataView }: Props) => {
  const { t } = useTranslation()
  const { testsTree } = useContext(TestsTreeContext)!

  const dispatch = useAppDispatch()
  const tableSettings = useAppSelector(selectSettings<TestTableParams>("table"))
  const treeSettings = useAppSelector(selectSettings<TestTreeParams>("tree"))
  const testsFilter = useAppSelector(selectFilter)
  const testsSelectedCount = useAppSelector(selectFilterCount)

  const [bulkUpdateTests, { isLoading }] = useBulkUpdateMutation()

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
    saveVisibleColumns(`tests-visible-cols-${key}`, newVisibleColumns)
  }

  const resetSelectedRows = () => {
    dispatch(
      updateSettings({
        key: "table",
        settings: {
          selectedRows: [],
          excludedRows: [],
          isAllSelectedTableBulk: false,
          hasBulk: false,
        },
      })
    )
  }

  const prepareBulkRequestData = () => {
    const commonFilters: Partial<TestGetFilters> = {
      is_archive: testsFilter.is_archive,
      last_status: testsFilter.statuses,
      search: testsFilter.name_or_id,
      labels: testsFilter.labels,
      not_labels: testsFilter.not_labels,
      labels_condition: testsFilter.labels_condition,
      suite: testsFilter.suites,
      plan: testsFilter.plans,
    }

    Object.keys(commonFilters).forEach((key) => {
      //@ts-ignore
      // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
      const v = commonFilters[key]
      if (Array.isArray(v)) {
        if (v.length) {
          const arr = v as string[]
          //@ts-ignore
          commonFilters[key] = arr.filter((item) => item !== "")
        }
        //@ts-ignore
        if ((commonFilters[key] as string[])?.length === 0) {
          //@ts-ignore
          delete commonFilters[key]
        }
      }
      if (v === undefined) {
        //@ts-ignore
        delete commonFilters[key]
      }
    })

    const reqData: TestBulkUpdate = {
      // @ts-ignore // TODO fix equial param plan in TestBulkUpdate and TestGetFilters
      filter_conditions: commonFilters,
      included_tests: [] as number[],
      excluded_tests: [] as number[],
      current_plan: Number(testPlanId),
    }
    if (tableSettings.isAllSelectedTableBulk) {
      reqData.excluded_tests = tableSettings.excludedRows
    } else {
      reqData.included_tests = tableSettings.selectedRows
    }

    return reqData
  }

  const handleMoveSubmit = async (plan: number) => {
    const reqData = prepareBulkRequestData()
    reqData.plan = plan
    const result = await bulkUpdateTests(reqData)
    //@ts-ignore
    if (result.error) {
      //@ts-ignore
      throw new Error(result.error as unknown)
    }
    resetSelectedRows()
  }

  const handleBulkAssignSubmit = async (assignee: string | null) => {
    const reqData = prepareBulkRequestData()
    reqData.assignee = assignee ?? ""
    const result = await bulkUpdateTests(reqData)
    // @ts-ignore
    if (result.error) {
      //@ts-ignore
      throw new Error(result.error as unknown)
    }
    resetSelectedRows()
  }

  const handleClearFilter = () => {
    dispatch(updateFilterSettings({ selected: null }))
    dispatch(clearFilter())
  }

  return (
    <Flex justify="space-between" align="flex-end" style={{ width: "100%", marginBottom: 24 }}>
      <Flex vertical gap={16}>
        <Flex align="center" wrap gap={16}>
          <Typography.Title level={2} style={{ marginBottom: 0, textWrap: "nowrap" }}>
            {t("Tests")}
          </Typography.Title>
          {tableSettings.hasBulk && dataView === "list" && (
            <Flex gap={8}>
              <MoveTests onSubmit={handleMoveSubmit} isLoading={isLoading} />
              <AssignTestsBulk onSubmit={handleBulkAssignSubmit} isLoading={isLoading} />
            </Flex>
          )}
        </Flex>
      </Flex>
      <Flex gap={8} wrap justify="flex-end" align="center">
        <Flex gap={8} align="center">
          <ClearFilters isVisible={!!testsSelectedCount} onClear={handleClearFilter} />
          <TestsButtonFilterDrawer />
          <TestsSavedFilters />
          <TestsSorter />
        </Flex>
        {!isList && (
          <Tooltip title={t("Collapse All")}>
            <Button
              icon={<CollapseIcon width={18} height={18} color="var(--y-sky-60)" />}
              onClick={() => testsTree.current?.closeAll()}
              data-testid="test-plan-detail-action-collapse-all-button"
            />
          </Tooltip>
        )}
        <SettingsColumnVisibility
          id={isList ? "tests-table-setting-columns-btn" : "tests-tree-setting-columns-btn"}
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

TestPlanDataActions.displayName = "TestPlanDataActions"
