export const filterAttributesByStatus = (
  attributes: Attribute[],
  statuses: Status[],
  watchStatus: number | null
) => {
  return attributes.filter((attr) => {
    if (!attr.status_specific?.length) {
      return true
    }

    const isAllStatusesAvailable = attr.status_specific?.length === statuses.length
    if (isAllStatusesAvailable) {
      return true
    }

    return watchStatus && attr.status_specific?.includes(watchStatus)
  })
}
