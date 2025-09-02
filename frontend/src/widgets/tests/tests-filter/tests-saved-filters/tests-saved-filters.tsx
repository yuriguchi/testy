import { Flex } from "antd"
import { MeContext } from "processes"
import { useContext, useMemo } from "react"

import { useAppDispatch, useAppSelector } from "app/hooks"

import {
  selectFilterSettings,
  testFilterSchema,
  updateFilter,
  updateFilterSettings,
} from "entities/test/model"

import { SavedFilters } from "features/filter"

import { ProjectContext } from "pages/project"

import { queryParamsBySchema } from "shared/libs/query-params"

export const TestsSavedFilters = () => {
  const { project } = useContext(ProjectContext)!
  const { userConfig } = useContext(MeContext)
  const dispatch = useAppDispatch()
  const testsSelectedFilter = useAppSelector(selectFilterSettings)

  const configFilters = userConfig?.test_plans?.filters?.[project.id]

  const handleChange = (value: string) => {
    const valueFilter = configFilters?.[value]

    const filterParse = queryParamsBySchema(testFilterSchema, { url: valueFilter })
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
        value={testsSelectedFilter.selected}
        onChange={handleChange}
      />
    </Flex>
  )
}
