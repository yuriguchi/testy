import { useEffect, useState } from "react"

// eslint-disable-next-line comma-spacing
const getFromLocalStorage = <T,>(key: string, parse?: (value: string) => T): T | null => {
  const localStorageValue = localStorage.getItem(key)

  if (localStorageValue === null) {
    return null
  }

  return parse?.(localStorageValue) ?? (localStorageValue as T)
}

// eslint-disable-next-line comma-spacing
export const useCacheState = <T,>(
  key: string,
  initialState: T | (() => T),
  parse?: (value: string) => T
): [T, (value: T) => void] => {
  const [cachedValue, setCachedValue] = useState<T>(getFromLocalStorage(key, parse) ?? initialState)

  const update = (value: T) => {
    setCachedValue(value)
    localStorage.setItem(key, String(value))
  }

  useEffect(() => {
    const valueFromLocalStorage = getFromLocalStorage<T>(key, parse)
    setCachedValue(valueFromLocalStorage ?? initialState)
  }, [])

  return [cachedValue, update]
}
