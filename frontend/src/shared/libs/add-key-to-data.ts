export const addKeyToData = <T extends BaseData>(data: T[]): DataWithKey<T>[] => {
  return data.map((item) => {
    return {
      ...item,
      key: String(item.id),
      children: item.children?.length ? addKeyToData(item.children) : [],
    }
  })
}
