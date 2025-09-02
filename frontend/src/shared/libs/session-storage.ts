export const savePrevPageSearch = (key: string, data: string) => {
  sessionStorage.setItem(key, data)
}

export const getPrevPageSearch = (key: string) => {
  return sessionStorage.getItem(key)
}

export const clearPrevPageSearch = (key: string) => {
  sessionStorage.removeItem(key)
}
