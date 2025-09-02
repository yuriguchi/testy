import { useStatuses } from "entities/status/model/use-statuses"
import { useCallback, useEffect, useMemo, useRef } from "react"
import { useParams } from "react-router-dom"

import { colors } from "shared/config"

import styles from "./styles.module.css"

interface UsePieProps {
  data: TestPlanStatistics[]
  type: "value" | "estimates"
  statuses: string[]
  updateStatuses: (statuses: string[]) => void
  period?: EstimatePeriod
  onHeightChange?: (height: number) => void
}

export const usePie = ({
  data,
  statuses,
  updateStatuses,
  type,
  period,
  onHeightChange,
}: UsePieProps) => {
  const { projectId, testPlanId } = useParams<ParamProjectId & ParamTestPlanId>()
  const { getStatusNumberByText, isLoading } = useStatuses({ project: projectId, plan: testPlanId })
  const chartRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    setTimeout(() => {
      if (!chartRef.current || !onHeightChange) {
        return
      }
      const legend = chartRef.current.querySelector(
        ".recharts-default-legend"
      ) as unknown as HTMLElement | null
      if (legend) {
        onHeightChange(legend.clientHeight + 50)
      }
    }, 0)
  }, [data])

  const getNewLastStatuses = (label: string) => {
    if (isLoading) {
      return []
    }
    const status = getStatusNumberByText(label)
    const isIncluded = status === null ? false : statuses.includes(status)
    const isOne = statuses.length === 1

    if (isIncluded) {
      return isOne ? [] : statuses.filter((i) => i !== status)
    }

    return [...statuses, status].filter(Boolean) as string[]
  }

  const isAllZero = useMemo(() => {
    return !data.some((item) => item[type] > 0)
  }, [data])

  const total = useMemo(() => {
    if (isAllZero) return 0
    return data.reduce((acc, cur) => acc + cur[type], 0)
  }, [data, isAllZero])

  const formatData = useMemo(() => {
    return data.map((item) => ({
      ...item,
      fill: item.color,
      [type]: isAllZero ? 1 : item[type],
    }))
  }, [data, isAllZero, isLoading])

  // TODO need refactoring
  const legendFormatter = useCallback(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (value: any, entry: any) => {
      // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
      const label = String(entry.payload.label)
      // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access
      const payloadValue = entry.payload[type]
      // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access
      const percent = entry.payload?.percent
      const lastStatuses = getNewLastStatuses(label)
      const isActive = checkActive(label)
      const estimateValue = type === "estimates" ? (period?.slice(0, 1) ?? "m") : ""

      const handleClick = () => {
        updateStatuses(lastStatuses)
      }

      if (isAllZero) {
        return (
          <span
            className={styles.legendTitle}
            style={{
              borderBottom: isActive ? `1px solid ${colors.accent}` : "0",
            }}
            onClick={handleClick}
            data-testid={`pie-legend-title-${label}`}
          >
            {label} <span className={styles.legendValue}>[0{estimateValue}] (0%)</span>
          </span>
        )
      }

      if (payloadValue === 0) {
        return (
          <span
            className={styles.legendTitle}
            style={{
              borderBottom: isActive ? `1px solid ${colors.accent}` : "0",
            }}
            onClick={handleClick}
            data-testid={`pie-legend-title-${label}`}
          >
            {label}{" "}
            <span className={styles.legendValue}>
              [{payloadValue ?? 0}
              {estimateValue}] (0%)
            </span>
          </span>
        )
      }

      return (
        <span
          className={styles.legendTitle}
          style={{
            borderBottom: isActive ? `1px solid ${colors.accent}` : "0",
          }}
          onClick={handleClick}
          data-testid={`pie-legend-title-${label}`}
        >
          {value}{" "}
          <span className={styles.legendValue}>
            [{payloadValue ?? 0}
            {estimateValue}] ({(percent * 100).toFixed(2)}%)
          </span>
        </span>
      )
    },
    [isAllZero, period, getStatusNumberByText]
  )

  const tooltipFormatter = useCallback(
    (value: number) => {
      if (isAllZero) return 0
      return value
    },
    [isAllZero]
  )

  const handleCellClick = (entry: { fill: string; value: number; label: string }) => {
    const lastStatuses = getNewLastStatuses(entry.label)
    updateStatuses(lastStatuses)
  }

  const checkActive = (label: string) => {
    const status = getStatusNumberByText(label)
    return statuses?.some((i) => String(i) === status) ?? false
  }

  return {
    formatData,
    total,
    legendFormatter,
    tooltipFormatter,
    handleCellClick,
    checkActive,
    chartRef,
  }
}
