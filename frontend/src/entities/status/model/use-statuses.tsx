import { useEffect, useMemo, useState } from "react"

import { useGetProjectQuery } from "entities/project/api"

import {
  useLazyGetTestPlanActivityStatusesQuery,
  useLazyGetTestPlanStatusesQuery,
} from "entities/test-plan/api"

import { useLazyGetStatusesQuery } from "../api"

interface Props {
  project?: string | number
  plan?: string | number | null
  isActivity?: boolean
}

const UNTESTED_NAME = "Untested"

export const useStatuses = ({ project, plan, isActivity }: Props) => {
  const [statuses, setStatuses] = useState<Status[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [getStatuses] = useLazyGetStatusesQuery()
  const [getStatusesFromTestPlan] = useLazyGetTestPlanStatusesQuery()
  const [getStatusesFromTestPlanActivity] = useLazyGetTestPlanActivityStatusesQuery()
  const { data: projectData } = useGetProjectQuery(Number(project), {
    skip: !project,
  })

  const fetchData = async () => {
    if (!project) return

    setIsLoading(true)

    let response = null
    if (isActivity && plan) {
      response = await getStatusesFromTestPlanActivity(plan)
    } else if (plan) {
      response = await getStatusesFromTestPlan(plan)
    } else {
      response = await getStatuses({ project })
    }
    setStatuses(response?.data ?? [])
    setIsLoading(false)
  }

  useEffect(() => {
    fetchData()
  }, [project, plan, isActivity])

  const convertToOption = (status: Status) => ({
    label: status.name,
    value: status.id,
    color: status.color,
    id: status.id,
  })

  const convertToFilter = (status: Status) => ({
    text: status.name,
    value: status.id.toString(),
  })

  const statusesOptions = statuses.map(convertToOption)
  const statusesOptionsWithUntested = [...statusesOptions, { label: UNTESTED_NAME, value: "null" }]

  const statusesFilters = statuses.map(convertToFilter)
  const statusesFiltersWithUntested = useMemo(
    () => [...statusesFilters, { text: UNTESTED_NAME, value: "null" }],
    [statuses]
  )

  const statusesObject = statuses.reduce(
    (acc, status) => {
      acc[status.id] = status.name
      return acc
    },
    {} as Record<number, string>
  )

  const allStatusesId = statuses.map((status) => status.id)

  const getStatusNumberByText = (value: string): string | null => {
    const findStatus = statusesFiltersWithUntested.find(
      (status) => status.text.toLowerCase() === value.toLowerCase()
    )

    return findStatus?.value ?? null
  }

  const getStatusById = (id: number) => {
    return statuses.find((status) => status.id === id) ?? null
  }

  const defaultStatus = projectData?.settings.default_status
    ? getStatusById(projectData.settings.default_status)
    : null

  return {
    statuses,
    statusesOptions,
    statusesObject,
    isLoading: isLoading || statuses.length === 0,
    allStatusesId,
    getStatusNumberByText,
    getStatusById,
    statusesOptionsWithUntested,
    statusesFilters,
    statusesFiltersWithUntested,
    refetch: fetchData,
    defaultStatus,
  }
}
