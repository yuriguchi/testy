import { Tooltip } from "antd"
import classNames from "classnames"
import { HtmlHTMLAttributes } from "react"
import { useTranslation } from "react-i18next"

import styles from "./styles.module.css"

interface Props extends HtmlHTMLAttributes<HTMLDivElement> {
  size?: "sm" | "md" | "lg"
}

const sizeStyles = {
  sm: 16,
  md: 24,
  lg: 32,
}

export const ArchivedTag = ({ className, style, size = "md", ...props }: Props) => {
  const { t } = useTranslation()
  return (
    <Tooltip title={t("Archived")}>
      <div
        className={classNames(styles.tag, className)}
        style={{
          minWidth: sizeStyles[size],
          minHeight: sizeStyles[size],
          width: sizeStyles[size],
          height: sizeStyles[size],
          lineHeight: `${sizeStyles[size]}px`,
          fontSize: sizeStyles[size] / 2,
          ...style,
        }}
        data-testid="archived-tag"
        {...props}
      >
        A
      </div>
    </Tooltip>
  )
}
