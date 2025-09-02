import { BarChartOutlined, PieChartOutlined } from "@ant-design/icons"
import { Row, Segmented } from "antd"
import { SegmentedValue } from "antd/lib/segmented"
import { MeContext } from "processes"
import { memo, useContext, useRef, useState } from "react"

import { useResizeObserver } from "shared/hooks"

import styles from "./styles.module.css"
import { TestPlanHistogram } from "./test-plan-histogram/test-plan-histogram"
import { TestPlanPieCount } from "./test-plan-pie-count"
import { TestPlanPieEstimates } from "./test-plan-pie-estimates/test-plan-pie-estimates"

interface Props {
  testPlanId?: number
}

export const TestPlanStatistics = memo(({ testPlanId }: Props) => {
  const graphsRef = useRef<HTMLDivElement>(null)
  const { userConfig, updateConfig } = useContext(MeContext)
  const [pieHeight, setPieHeight] = useState(208)

  const handlePieHeightChange = (height: number) => {
    if (height > pieHeight) {
      setPieHeight(height)
    }
  }

  const [directionPies, setDirectionPies] = useState<"row" | "column">("row")
  useResizeObserver({
    elRef: graphsRef,
    onResize: (_, width) => {
      setDirectionPies(width <= 800 ? "column" : "row")
    },
  })

  const [segment, setSegment] = useState<SegmentedValue>(userConfig?.ui?.graph_base_type ?? "pie")

  const handleSegmentedChange = async (value: SegmentedValue) => {
    setSegment(value)
    await updateConfig({
      ...userConfig,
      ui: {
        ...userConfig?.ui,
        graph_base_type: value,
      },
    })
  }

  return (
    <div style={{ marginBottom: 8 }}>
      <Row align="middle" justify="end" style={{ marginBottom: 8 }}>
        <Segmented
          id="test-plan-statistic-tabs"
          style={{ position: "absolute" }}
          options={[
            {
              value: "pie",
              icon: <PieChartOutlined data-testid="pie-chart-icon" />,
            },
            {
              value: "bar",
              icon: <BarChartOutlined data-testid="bar-chart-icon" />,
            },
          ]}
          onChange={handleSegmentedChange}
          size="middle"
          defaultValue={segment}
          value={segment}
        />
      </Row>
      <div
        className={styles.graphsBlock}
        style={{
          flexDirection: directionPies,
        }}
        ref={graphsRef}
      >
        {segment === "pie" && (
          <>
            <TestPlanPieCount
              testPlanId={testPlanId}
              onHeightChange={handlePieHeightChange}
              height={pieHeight}
            />
            <TestPlanPieEstimates
              testPlanId={testPlanId}
              onHeightChange={handlePieHeightChange}
              height={pieHeight}
            />
          </>
        )}
        {segment === "bar" && <TestPlanHistogram testPlanId={testPlanId} />}
      </div>
    </div>
  )
})

TestPlanStatistics.displayName = "TestPlanStatistics"
