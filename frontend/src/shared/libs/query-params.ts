export type QuryParamsSchema = Record<
  string,
  {
    format?: (value: string) => unknown
    default?: unknown
  }
>

type InferSchema<T> = {
  [K in keyof T]: T[K] extends { format: (value: string) => infer R }
    ? T[K] extends { default: infer D }
      ? R | D
      : R
    : T[K] extends { default: infer D }
      ? D
      : never
}

interface QueryParamsBySchemaOptions {
  url?: string
  ignoredUnscheme?: boolean
}

export const queryParamsBySchema = <T extends QuryParamsSchema>(
  schema: T,
  options: QueryParamsBySchemaOptions = {}
): InferSchema<T> => {
  const params = new URLSearchParams(options.url ?? window.location.search)
  const { ignoredUnscheme = true } = options

  const formattedData = Object.entries(schema).reduce(
    (acc, [key, { format, default: defaultValue }]) => {
      const rawValue = params.get(key)
      let value: InferSchema<T>[typeof key] | undefined

      if (rawValue !== null) {
        value = format
          ? (format(rawValue) as InferSchema<T>[string] | undefined)
          : (rawValue as InferSchema<T>[typeof key])
      } else if (defaultValue !== undefined) {
        value = defaultValue as InferSchema<T>[string] | undefined
      } else {
        value = undefined
      }

      acc[key as keyof T] = value!
      return acc
    },
    {} as InferSchema<T>
  )

  if (!ignoredUnscheme) {
    params.forEach((value, key) => {
      if (!(key in schema)) {
        // @ts-ignore
        formattedData[key] = value
      }
    })
  }

  return formattedData
}
