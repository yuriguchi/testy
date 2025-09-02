import { FetchBaseQueryError } from "@reduxjs/toolkit/dist/query"
import { DatePicker, Progress, Tooltip } from "antd"
import { ColumnsType } from "antd/lib/table"
import dayjs, { Dayjs } from "dayjs"
import { NoUndefinedRangeValueType, RangePickerProps } from "rc-picker/lib/PickerInput/RangePicker"
import { useEffect, useState } from "react"
import { useTranslation } from "react-i18next"
import { Link, useParams } from "react-router-dom"

import { useLazyGetProjectProgressQuery } from "entities/project/api"

import { colors, formatBaseDate } from "shared/config"

interface ProgressItemProps extends HTMLDataAttribute {
  percent: number
  countStr: string
}

const ProgressItem = ({ percent, countStr, ...props }: ProgressItemProps) => {
  return (
    <div {...props}>
      <div style={{ display: "flex", alignItems: "center", flexDirection: "row" }}>
        <Progress percent={percent} strokeColor={colors.accent} showInfo={false} />
        <span style={{ marginLeft: 6, fontSize: 14 }}>{percent}%</span>
      </div>
      <div style={{ display: "flex", flexDirection: "column", fontSize: 12 }}>
        <span>{countStr}</span>
      </div>
    </div>
  )
}

export const useProjectOverviewProgress = () => {
  const { t } = useTranslation()
  const { projectId } = useParams<ParamProjectId>()
  const [getProgress, { data }] = useLazyGetProjectProgressQuery()
  const [isLoading, setIsLoading] = useState(false)

  const disabledDateStart = (current: Dayjs) => {
    return !current.isBefore(dayjs())
  }

  const handleChange = async (values: NoUndefinedRangeValueType<Dayjs>) => {
    if (!values || !projectId) return
    const [dateStart, dateEnd] = values
    if (!dateStart || !dateEnd) return

    try {
      setIsLoading(true)
      await getProgress({
        projectId,
        period_date_start: formatBaseDate(dateStart),
        period_date_end: formatBaseDate(dateEnd),
      })
    } catch (err) {
      const error = err as FetchBaseQueryError
      console.error(error)
    } finally {
      setIsLoading(false)
    }
  }

  const columns: ColumnsType<ProjectsProgress> = [
    {
      title: t("Test Plans"),
      dataIndex: "title",
      key: "title",
      ellipsis: {
        showTitle: false,
      },
      render: (_, record) => {
        return (
          <Link
            id={`overview-test-plan-link-${record.title}`}
            to={`/projects/${projectId}/plans/${record.id}`}
          >
            <Tooltip placement="topLeft" title={record.title}>
              {record.title}
            </Tooltip>
          </Link>
        )
      },
    },
    {
      title: t("Total"),
      dataIndex: "tests_total",
      key: "tests_total",
      width: "180px",
      render: (_, record) => {
        const percent = Math.round(
          (Number(record.tests_progress_total) / Number(record.tests_total)) * 100
        )
        const countStr = `${record.tests_progress_total} / ${record.tests_total}`

        return (
          <ProgressItem
            percent={record.tests_progress_total ? percent : 0}
            countStr={countStr}
            data-testid={`${record.title}-progress-item`}
          />
        )
      },
    },
    {
      title: (
        <DatePicker.RangePicker
          defaultValue={[dayjs().subtract(7, "days"), dayjs()]}
          onChange={handleChange as RangePickerProps<Dayjs>["onChange"]}
          disabledDate={disabledDateStart}
          size="small"
          data-testid="project-overview-progress-date-picker"
        />
      ),
      dataIndex: "tests_progress_period",
      key: "tests_progress_period",
      width: "250px",
      render: (_, record) => {
        const percent = Math.round(
          (Number(record.tests_progress_period) / Number(record.tests_progress_total)) * 100
        )
        return (
          <ProgressItem
            percent={record.tests_progress_total ? percent : 0}
            countStr={String(record.tests_progress_period)}
            data-testid={`${record.title}-progress-period-item`}
          />
        )
      },
    },
  ]

  useEffect(() => {
    if (!projectId) return
    setIsLoading(true)
    getProgress({
      projectId,
      period_date_start: formatBaseDate(dayjs().subtract(7, "days")),
      period_date_end: formatBaseDate(dayjs()),
    }).finally(() => {
      setIsLoading(false)
    })
  }, [projectId])

  return {
    columns,
    data,
    isLoading,
    handleChange,
    disabledDateStart,
  }
}
