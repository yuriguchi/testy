import { InfoCircleOutlined } from "@ant-design/icons"
import { Tooltip } from "antd"

export const InfoTooltipBtn = ({ title }: { title: string }) => {
  return (
    <Tooltip title={title}>
      <InfoCircleOutlined style={{ color: "rgba(0,0,0,.45)", marginLeft: 4 }} />
    </Tooltip>
  )
}
