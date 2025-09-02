import { Flex, Switch, SwitchProps, Typography } from "antd"
import { SwitchSize } from "antd/es/switch"
import React from "react"

interface SwitcherProps {
  fontSize: number
  lineHeight: string
  switcher: SwitchSize
}

interface SizerProps {
  sm: SwitcherProps
  lg: SwitcherProps
}

type Props = {
  id: string
  label: string | React.ReactNode
  labelFontSize?: number
  size?: "sm" | "lg"
} & Omit<SwitchProps, "size">

const sizer: SizerProps = {
  sm: { fontSize: 14, lineHeight: "22px", switcher: "small" },
  lg: { fontSize: 16, lineHeight: "24px", switcher: "default" },
}

export const Toggle = ({ id, label, labelFontSize = 16, size = "sm", ...props }: Props) => {
  return (
    <Flex gap={6} align="center" style={{ cursor: "pointer", width: "fit-content" }}>
      <Switch id={id} size={sizer[size].switcher} {...props} />
      {typeof label === "string" ? (
        <label htmlFor={id} style={{ cursor: "pointer" }}>
          <Typography.Text
            style={{ fontSize: labelFontSize, lineHeight: "24px", color: "var(--y-sky-80)" }}
          >
            {label}
          </Typography.Text>
        </label>
      ) : (
        <label htmlFor={id} style={{ cursor: "pointer" }}>
          {label}
        </label>
      )}
    </Flex>
  )
}
