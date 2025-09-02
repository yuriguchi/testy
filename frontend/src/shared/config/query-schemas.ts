export const paginationSchema = {
  page: {
    format: (value: string) => Number(value),
    default: 1,
  },
  page_size: {
    format: (value: string) => Number(value),
    default: 10,
  },
}

export const orderingSchema = (defaultValue = "name") => ({
  ordering: {
    default: defaultValue,
  },
})
