import { useEffect, useState } from "react"

export function useDebounce<T>(value: T, delay?: number, skipInit = false): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)
  const [isSkipInit, setIsSkipInit] = useState(skipInit)

  useEffect(() => {
    const timer = setTimeout(() => {
      if (isSkipInit) {
        setIsSkipInit(false)
        return
      }
      setDebouncedValue(value)
    }, delay ?? 500)

    return () => {
      clearTimeout(timer)
    }
  }, [value, delay])

  return debouncedValue
}
