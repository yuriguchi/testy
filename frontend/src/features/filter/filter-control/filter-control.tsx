import { Flex, Modal, notification } from "antd"
import { MeContext } from "processes"
import { useContext, useEffect } from "react"
import { useTranslation } from "react-i18next"

import { ProjectContext } from "pages/project"

import { deepEqualObjects } from "shared/libs"
import { QuryParamsSchema, queryParamsBySchema } from "shared/libs/query-params"

import { ActionButtonsFilter } from "./ui/action-buttons-filter/action-buttons-filter"
import { SelectFilter } from "./ui/select-filter/select-filter"

interface Props {
  type: "plans" | "suites"
  hasSomeFilter: boolean
  filterData: Record<string, unknown>
  filterSchema: QuryParamsSchema
  filterSettings: FilterSettings
  updateFilter: (filter: Record<string, unknown>) => void
  updateSettings: (settings: Partial<FilterSettings>) => void
  clearFilter: () => void
}

export const FilterControl = ({
  type,
  hasSomeFilter,
  filterData,
  filterSchema,
  filterSettings,
  updateFilter,
  updateSettings,
  clearFilter,
}: Props) => {
  const { t } = useTranslation()

  const { userConfig, updateConfig } = useContext(MeContext)
  const { project } = useContext(ProjectContext)!

  const configFilters =
    type === "plans"
      ? userConfig?.test_plans?.filters?.[project.id]
      : userConfig?.test_suites?.filters?.[project.id]

  const handleDelete = (name: string) => {
    Modal.confirm({
      title: t("Do you want to delete this filter?"),
      okText: t("Delete"),
      cancelText: t("Cancel"),
      onOk: async () => {
        const filtersData = { ...(configFilters ?? {}) }
        delete filtersData[name]

        const typeKey = type === "plans" ? "test_plans" : "test_suites"
        await updateConfig({
          ...userConfig,
          [typeKey]: {
            ...userConfig?.[typeKey],
            filters: {
              [project.id]: {
                ...filtersData,
              },
            },
          },
        })

        if (filterSettings.selected === name) {
          updateSettings({ selected: null })
          clearFilter()
        }

        notification.success({
          message: t("Success"),
          closable: true,
          description: t("Filter deleted successfully"),
        })
      },
      okButtonProps: { "data-testid": "delete-filter-button-confirm" },
      cancelButtonProps: { "data-testid": "delete-filter-button-cancel" },
    })
  }

  const handleSelect = (name: string) => {
    const value = configFilters?.[name]
    const filterParse = queryParamsBySchema(filterSchema, { url: value })
    updateFilter(filterParse)
  }

  const handleResetToSelected = () => {
    if (!filterSettings.selected) {
      return
    }
    const value = configFilters?.[filterSettings.selected]
    const filterParse = queryParamsBySchema(filterSchema, { url: value })
    updateFilter(filterParse)
  }

  useEffect(() => {
    if (!hasSomeFilter || !configFilters || filterSettings.selected) {
      return
    }

    const urlParse = queryParamsBySchema(filterSchema)
    for (const [filterName, filterValue] of Object.entries(configFilters)) {
      const filterParse = queryParamsBySchema(filterSchema, { url: filterValue })
      const isEqualUrlFilter = deepEqualObjects(urlParse, filterParse)
      if (isEqualUrlFilter) {
        updateSettings({ selected: filterName })
        return
      }
    }
  }, [hasSomeFilter, configFilters, filterSettings.selected])

  return (
    <Flex align="center" justify="space-between" style={{ width: "100%" }}>
      <SelectFilter
        type={type}
        filterData={filterData}
        filterSettings={filterSettings}
        configFilters={configFilters}
        filterSchema={filterSchema}
        onDelete={handleDelete}
        onSelect={handleSelect}
        updateSettings={updateSettings}
      />
      <ActionButtonsFilter
        type={type}
        filterData={filterData}
        filterSettings={filterSettings}
        onDelete={handleDelete}
        updateSettings={updateSettings}
        resetFilterToSelected={handleResetToSelected}
        clearFilter={clearFilter}
      />
    </Flex>
  )
}
