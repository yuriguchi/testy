import classNames from "classnames"

import { icons } from "shared/assets/inner-icons"

import styles from "./styles.module.css"

const { DotsIcon } = icons

interface Props {
  direction?: "left" | "right"
  onMouseDown: React.MouseEventHandler<HTMLDivElement>
}

export const ResizeLine = ({ direction = "right", onMouseDown }: Props) => {
  return (
    <div className={classNames(styles.resizeLine, styles[direction])} onMouseDown={onMouseDown}>
      <DotsIcon width={10} height={23} style={{ color: "var(--y-grey-30)" }} />
    </div>
  )
}
