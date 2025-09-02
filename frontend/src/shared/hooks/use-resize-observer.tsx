import { useEffect } from "react"

interface Props {
  elRef: React.RefObject<HTMLElement>
  onResize: (elRef: React.RefObject<HTMLElement>, width: number) => void
}

export const useResizeObserver = ({ elRef, onResize }: Props) => {
  useEffect(() => {
    if (!elRef.current) return
    const resizeObserver = new ResizeObserver(() => {
      if (!elRef.current) return
      onResize(elRef, elRef.current.offsetWidth)
    })
    resizeObserver.observe(elRef.current)
    return () => resizeObserver.disconnect()
  }, [])
}
