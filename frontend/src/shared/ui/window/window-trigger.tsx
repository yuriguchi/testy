import { ReactNode, isValidElement } from "react"

interface Props {
  asChild?: boolean
  children: ReactNode
  onClick?: () => void
}

export const WindowTrigger = ({ children, onClick, asChild }: Props) => {
  if (asChild && isValidElement(children)) {
    return children
  }

  return <button onClick={onClick}>{children}</button>
}
