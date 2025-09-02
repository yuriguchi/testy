import cn from "classnames"
import { HTMLProps, PropsWithChildren } from "react"

import styles from "./styles.module.css"

type Props = HTMLProps<HTMLDivElement> & PropsWithChildren

export const LayoutView = ({ className, children, ...props }: Props) => {
  return (
    <div className={cn(styles.wrapper, className)} {...props}>
      {children}
    </div>
  )
}
