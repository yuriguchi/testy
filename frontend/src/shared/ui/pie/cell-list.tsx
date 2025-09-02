import { Cell } from "recharts"

import { colors } from "shared/config"

interface Entry {
  fill: string
  label: string
  value: number
  estimates: number
  empty_estimates: number
}

interface Props {
  data: Entry[]
  handleCellClick: (entry: Entry) => void
  checkActive: (label: string) => boolean
}

export const PieCellList = ({ data, handleCellClick, checkActive }: Props) => {
  return (
    <>
      {data.map((entry) => (
        <Cell
          style={{ cursor: "pointer" }}
          key={`cell-${entry.label}`}
          fill={entry.fill}
          stroke={(checkActive(entry.label) && colors.accent) || undefined}
          onClick={handleCellClick ? () => handleCellClick(entry) : undefined}
        />
      ))}
    </>
  )
}
