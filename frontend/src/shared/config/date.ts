import { Dayjs } from "dayjs"

export const formatBaseDate = (date: Dayjs) => {
  return date.format("YYYY-MM-DD").toString()
}
