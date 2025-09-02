import classNames from "classnames"
import { CSSProperties } from "react"

import styles from "./styles.module.css"

interface Props {
  shape?: "circle" | "rect"
  width?: number | string
  height?: number | string
  style?: CSSProperties
  className?: string
}

export const Skeleton = ({
  shape = "rect",
  width = "100%",
  height = "100%",
  style,
  className,
}: Props) => {
  return (
    <div
      className={classNames(styles.skeleton, { [styles.circle]: shape === "circle" }, className)}
      style={{ width, minHeight: height, height, ...style }}
    />
  )
}
