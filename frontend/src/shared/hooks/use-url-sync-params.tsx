import { useEffect, useState } from "react"
import { useSearchParams } from "react-router-dom"

import { deepEqualObjects } from "shared/libs"
import { QuryParamsSchema, queryParamsBySchema } from "shared/libs/query-params"

interface Props<T extends Record<string, unknown>> {
  params: T
  queryParamsSchema: QuryParamsSchema
  updateParams?: (params: Partial<T>) => void
}

export const useUrlSyncParams = <T extends Record<string, unknown>>({
  params,
  queryParamsSchema,
  updateParams,
}: Props<T>) => {
  const [skipInit, setSkipInit] = useState(true)
  const [searchParams, setSearchParams] = useSearchParams()

  useEffect(() => {
    if (!skipInit) {
      const urlParseBySchema = queryParamsBySchema(queryParamsSchema)
      const isEqualObject = deepEqualObjects(urlParseBySchema, params)
      if (isEqualObject) {
        return
      }

      for (const [key, value] of Object.entries(params)) {
        if (
          value === undefined ||
          (Array.isArray(value) && !value.length) ||
          (typeof value === "string" && !value.length)
        ) {
          searchParams.delete(key)
          continue
        }

        searchParams.set(key, String(value))
      }
      setSearchParams(searchParams)
    } else {
      setSkipInit(false)
    }
  }, [params])

  useEffect(() => {
    if (!updateParams || skipInit) {
      return
    }

    const urlParseBySchema = queryParamsBySchema(queryParamsSchema)
    const isEqualObject = deepEqualObjects(urlParseBySchema, params)
    if (isEqualObject) {
      return
    }

    updateParams(params as Partial<T>)
  }, [skipInit, params, searchParams.toString()])
}
