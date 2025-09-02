import { useTranslation } from "react-i18next"
import { Label, Legend, PieChart, Pie as PieRechart, ResponsiveContainer, Tooltip } from "recharts"

import { PieCellList } from "./cell-list"
import { usePie } from "./model/use-pie"

interface PieProps {
  data: TestPlanStatistics[]
  statuses: string[]
  updateStatuses: (statuses: string[]) => void
  type: "value" | "estimates"
  height?: number
  onHeightChange?: (height: number) => void
}

export const Pie = ({
  data,
  statuses,
  updateStatuses,
  type,
  height = 208,
  onHeightChange,
}: PieProps) => {
  const { t } = useTranslation()
  const {
    formatData,
    total,
    legendFormatter,
    tooltipFormatter,
    handleCellClick,
    checkActive,
    chartRef,
  } = usePie({
    data: data ?? [],
    statuses,
    updateStatuses,
    type,
    onHeightChange,
  })

  return (
    <ResponsiveContainer width="100%" height={height} ref={chartRef}>
      <PieChart>
        <PieRechart
          data={formatData}
          dataKey={type}
          nameKey="label"
          cx="50%"
          cy="50%"
          innerRadius={80}
          outerRadius={94}
          fill="#a0a0a0"
        >
          <PieCellList
            data={formatData}
            checkActive={checkActive}
            handleCellClick={handleCellClick}
          />
          <Label position="centerBottom" fontSize={26} value={t("Total")} />
          <Label
            value={total}
            position="centerTop"
            offset={20}
            fontSize={28}
            style={{ marginTop: 20 }}
            dy={12}
            fill="#000"
            fontWeight="bold"
          />
        </PieRechart>
        <Legend
          iconSize={10}
          layout="vertical"
          verticalAlign="middle"
          align="right"
          iconType="circle"
          formatter={legendFormatter}
        />
        <Tooltip formatter={tooltipFormatter} />
      </PieChart>
    </ResponsiveContainer>
  )
}
