import { Flex } from "antd"
import { MeContext } from "processes"
import { useContext, useMemo } from "react"

import { useAppDispatch, useAppSelector } from "app/hooks"

import {
  selectFilterSettings,
  testCasesFilterSchema,
  updateFilter,
  updateFilterSettings,
} from "entities/test-case/model"

import { SavedFilters } from "features/filter"

import { ProjectContext } from "pages/project"

import { queryParamsBySchema } from "shared/libs/query-params"

export const TestCasesSavedFilters = () => {
  const { project } = useContext(ProjectContext)!
  const { userConfig } = useContext(MeContext)
  const dispatch = useAppDispatch()
  const testCasesSelectedFilter = useAppSelector(selectFilterSettings)
  const configFilters = userConfig?.test_suites?.filters?.[project.id]

  const handleChange = (value: string) => {
    const valueFilter = configFilters?.[value]

    const filterParse = queryParamsBySchema(testCasesFilterSchema, { url: valueFilter })
    dispatch(updateFilterSettings({ selected: value }))
    dispatch(updateFilter(filterParse as Record<string, unknown>))
  }

  const configFiltersKeys = useMemo(() => {
    if (!configFilters) {
      return []
    }

    return Object.keys(configFilters)
  }, [userConfig])

  if (!configFiltersKeys.length) {
    return null
  }

  return (
    <Flex align="center">
      <SavedFilters
        options={configFiltersKeys}
        value={testCasesSelectedFilter.selected}
        onChange={handleChange}
      />
    </Flex>
  )
}
