import dayjs, { Dayjs } from "dayjs"
import isSameOrAfter from "dayjs/plugin/isSameOrAfter"
import isSameOrBefore from "dayjs/plugin/isSameOrBefore"
import { useState } from "react"

dayjs.extend(isSameOrAfter)
dayjs.extend(isSameOrBefore)

export const useDatepicker = () => {
  const [dateTo, setDateTo] = useState<Dayjs | null>(dayjs())
  const [dateFrom, setDateFrom] = useState<Dayjs | null>(dayjs())

  const disabledDateFrom = (current: Dayjs) => {
    return current.isSameOrAfter(dateTo)
  }

  const disabledDateTo = (current: Dayjs) => {
    return current.isSameOrBefore(dateFrom)
  }

  return {
    dateTo,
    dateFrom,
    setDateTo,
    setDateFrom,
    disabledDateFrom,
    disabledDateTo,
  }
}
