import classNames from "classnames"
import { ReactNode } from "react"

import styles from "./styles.module.css"
import { useWindowContext } from "./window"

interface Props {
  children: (props: {
    onClose: () => void
    onHide: () => void
    onOpen: () => void
    onExpand: () => void
    open: boolean
    hide: boolean
    expand: boolean
  }) => ReactNode
}

const TRIGGER_NAME = "WindowBar"
export const WindowBar = ({ children }: Props) => {
  const context = useWindowContext(TRIGGER_NAME)

  const onExpand = () => {
    if (context.expand) {
      const newSize = context.minSize ?? context.defaultSize
      context.setSize({ width: newSize.width, height: "auto" })
      context.onExpandChange(false)
      return
    }

    context.setSize({ width: window.innerWidth, height: window.innerHeight })
    context.setPos({ x: 0, y: 0 })
    context.onExpandChange(true)
    context.onHideChange(false)
  }

  const handleDoubleClickBar = () => {
    onExpand()
  }

  const handleHide = () => {
    if (context.hide) {
      context.setSize(context.defaultSize)
      context.onHideChange(false)
      return
    }

    const newSize = context.minSize ?? context.defaultSize
    context.onHideChange(true)
    context.setMinSize({ width: newSize.width, height: 50 })
    context.setSize({ width: context.size.width, height: 50 })
  }

  if (!context.open) {
    return null
  }

  return (
    <div
      className={classNames(styles.windowBar, { [styles.noBorder]: context.hide })}
      onDoubleClick={handleDoubleClickBar}
    >
      {children({
        onClose: () => context.onOpenChange(false),
        onOpen: () => context.onOpenChange(true),
        onHide: handleHide,
        onExpand,
        open: context.open,
        hide: context.hide,
        expand: context.expand,
      })}
    </div>
  )
}
