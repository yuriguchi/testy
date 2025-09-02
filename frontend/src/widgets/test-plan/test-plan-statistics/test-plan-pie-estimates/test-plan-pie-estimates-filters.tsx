import { Select } from "antd"
import { useTranslation } from "react-i18next"

const PERIODS = [
  { label: "minutes", value: "minutes" },
  { label: "hours", value: "hours" },
  { label: "days", value: "days" },
]

interface Props {
  setPeriod: (period: EstimatePeriod) => void
  value: EstimatePeriod
}

export const TestPlanPieEstimatesFilters = ({ setPeriod, value }: Props) => {
  const { t } = useTranslation()

  const handleChange = (newValue: string) => {
    setPeriod(newValue as EstimatePeriod)
  }

  return (
    <div
      style={{
        marginLeft: 14,
        display: "flex",
        alignItems: "center",
      }}
      data-testid="test-plan-pie-estimates-filters"
    >
      <Select
        placeholder={t("Please select")}
        value={value}
        style={{ width: "100%", minWidth: 120, height: 32 }}
        options={PERIODS}
        size="middle"
        defaultActiveFirstOption
        onChange={handleChange}
      />
    </div>
  )
}
