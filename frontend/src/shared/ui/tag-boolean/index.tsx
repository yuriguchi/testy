import { Tag } from "antd"

import { colors } from "shared/config"

interface TagBooleanProps {
  value: boolean
  trueText: string
  falseText: string
  dataTestid?: string
}

export const TagBoolean = ({ value, trueText, falseText, dataTestid }: TagBooleanProps) => {
  return value ? (
    <Tag color={colors.success} data-testid={dataTestid}>
      {trueText}
    </Tag>
  ) : (
    <Tag color={colors.error} data-testid={dataTestid}>
      {falseText}
    </Tag>
  )
}
