import { createPortal } from "react-dom"

interface Props {
  children: React.ReactNode
  id: string
}

export const Portal = ({ children, id }: Props) => {
  const el = document.getElementById(id)
  if (!el) {
    return createPortal(children, document.body)
  }

  return createPortal(children, el)
}
