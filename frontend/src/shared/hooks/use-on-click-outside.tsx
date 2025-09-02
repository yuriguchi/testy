import { RefObject, useCallback, useEffect } from "react"

type Event = MouseEvent | TouchEvent

export const useOnClickOutside = <T extends HTMLElement = HTMLElement>(
  ref: RefObject<T>,
  handler: (event: Event) => void,
  isEnable = true,
  ignoredList: string[] = []
) => {
  const listener = useCallback(
    (event: Event) => {
      const el = ref?.current
      if (!el) {
        return
      }

      const targetElement = event?.target as Element
      const hasIgnored = ignoredList.some((item) => targetElement?.closest(item))

      if (el.contains(targetElement ?? null) || hasIgnored) {
        return
      }

      handler(event)
    },
    [ref, handler]
  )

  useEffect(() => {
    if (!isEnable) {
      return
    }

    document.addEventListener("mousedown", listener)
    document.addEventListener("touchstart", listener)

    return () => {
      document.removeEventListener("mousedown", listener)
      document.removeEventListener("touchstart", listener)
    }
  }, [ref, handler, isEnable])

  useEffect(() => {
    if (!isEnable) {
      document.removeEventListener("mousedown", listener)
      document.removeEventListener("touchstart", listener)
    }
  }, [isEnable])
}
