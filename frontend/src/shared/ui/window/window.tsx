import { ReactNode, useEffect, useRef, useState } from "react"

import { useControllableState } from "shared/hooks/use-controllable-state"
import { createContext } from "shared/libs/create-context"

interface Size {
  width: string | number
  height: string | number
}

interface Position {
  x: number
  y: number
}

interface WindowContextValue {
  triggerRef: React.RefObject<HTMLButtonElement>
  contentRef: React.RefObject<HTMLDivElement>
  open: boolean
  expand: boolean
  isLoading: boolean
  hide: boolean
  size: Size
  defaultSize: Size
  pos: Position
  onOpenChange(open: boolean): void
  onExpandChange: (toggle: boolean) => void
  onHideChange(hide: boolean): void
  setSize: (size: Size) => void
  setMinSize: (size: Size) => void
  setPos: (size: Position) => void
  setIsLoading: (isLoading: boolean) => void
  minSize?: Size
}
const WINDOW_NAME = "Window"
const [WindowProvider, useWindowContextFn] = createContext<WindowContextValue>(WINDOW_NAME)

interface Props {
  children: ReactNode
  open: boolean
  isLoading?: boolean
  defaultSize?: Size
  minSize?: Size
  defaultPos?: Position
  defaultOpen?: boolean
  expand?: boolean
  onOpenChange?: (toggle: boolean) => void
  onExpandChange?: (toggle: boolean) => void
}

export const useWindowContext = useWindowContextFn
const centerY = document.body.offsetHeight / 2
const centerX = document.body.offsetWidth / 2
const DEFAULT_SIZE: Size = { height: "fit-content", width: "fit-content" }
const DEFAULT_POS: Position = { x: centerX, y: centerY }

export const Window = ({
  children,
  defaultOpen = false,
  open: propOpen = false,
  isLoading: propIsLoading = false,
  expand: propExpand = false,
  defaultSize = DEFAULT_SIZE,
  minSize: propMinSize,
  defaultPos = DEFAULT_POS,
  onOpenChange,
}: Props) => {
  const triggerRef = useRef<HTMLButtonElement>(null)
  const contentRef = useRef<HTMLDivElement>(null)

  const [hide, setHide] = useState(false)
  const [size, setSize] = useState<Size>(defaultSize)
  const [minSize, setMinSize] = useState<Size>(propMinSize ?? DEFAULT_SIZE)
  const [pos, setPos] = useState<Position>(defaultPos)

  const [isLoading, setIsLoading] = useState(propIsLoading)
  const [expand, setExpand] = useState(propExpand)

  const [open = false, setOpen] = useControllableState({
    prop: propOpen,
    defaultProp: propOpen,
    onChange: onOpenChange,
  })

  useEffect(() => {
    setOpen(defaultOpen)
  }, [defaultOpen])

  return (
    <WindowProvider
      triggerRef={triggerRef}
      contentRef={contentRef}
      open={open}
      isLoading={isLoading}
      expand={expand}
      hide={hide}
      size={size}
      pos={pos}
      setSize={setSize}
      setPos={setPos}
      setMinSize={setMinSize}
      setIsLoading={setIsLoading}
      onHideChange={setHide}
      onOpenChange={setOpen}
      onExpandChange={setExpand}
      minSize={minSize}
      defaultSize={defaultSize}
    >
      {children}
    </WindowProvider>
  )
}
