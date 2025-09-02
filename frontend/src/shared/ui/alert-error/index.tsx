import { Alert } from "antd"

import { ErrorObj, useAlertError } from "shared/hooks"

interface AlertErrorProps {
  error: ErrorObj
  skipFields?: string[]
  style?: React.CSSProperties
}

export const AlertError = ({ error, skipFields, style }: AlertErrorProps) => {
  const errors = useAlertError(error, skipFields)

  return (
    errors && (
      <Alert
        style={{ marginBottom: 24, ...style }}
        description={errors.errors ?? JSON.stringify(errors)}
        type="error"
      />
    )
  )
}
