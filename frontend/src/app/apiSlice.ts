import { fetchBaseQuery } from "@reduxjs/toolkit/dist/query/react"
import type { BaseQueryFn, FetchArgs, FetchBaseQueryError } from "@reduxjs/toolkit/query"
import { Mutex } from "async-mutex"

import { getCsrfCookie } from "entities/auth/api"
import { logout } from "entities/auth/model"

import { config } from "shared/config"
import { savePrevPageUrl } from "shared/libs"

import { handleError } from "./slice"

export const authMutex = new Mutex()

const createQuery = (baseUrl: string) => {
  return fetchBaseQuery({
    baseUrl,
    credentials: "include",
    prepareHeaders: (headers) => {
      const csrfToken = getCsrfCookie()
      if (csrfToken) {
        headers.set("X-CSRFToken", csrfToken)
      }
      return headers
    },
  })
}

const baseQuery = createQuery(`${config.apiRoot}/api/${config.apiVersion}/`)

export const authQuery = createQuery(`${config.apiRoot}/auth/`)

export const baseQueryAuth: BaseQueryFn<string | FetchArgs, unknown, FetchBaseQueryError> = async (
  args,
  api,
  extraOptions
) => {
  await authMutex.waitForUnlock()

  const result = await authQuery(args, api, extraOptions)

  if (result.error?.status === 404) {
    await authMutex.waitForUnlock()
    api.dispatch(handleError({ code: 404, message: "Sorry, the page you visited does not exist." }))
  }

  return result
}

export const baseQueryWithLogout: BaseQueryFn<
  string | FetchArgs,
  unknown,
  FetchBaseQueryError
> = async (args, api, extraOptions) => {
  await authMutex.waitForUnlock()

  let result = await baseQuery(args, api, extraOptions)

  if (result.error?.status === 404) {
    await authMutex.waitForUnlock()
    api.dispatch(handleError({ code: 404, message: "Sorry, the page you visited does not exist." }))
  }

  if (result?.error?.status === 403 && result?.meta?.request.redirect !== "manual") {
    api.dispatch(
      handleError({ code: 403, message: "You do not have permission to access this page." })
    )
  }

  if (result?.error?.status === 401 && window.location.pathname !== "/login") {
    if (!authMutex.isLocked()) {
      const release = await authMutex.acquire()
      try {
        await authQuery("logout/", api, extraOptions)
      } finally {
        savePrevPageUrl(window.location.pathname)
        window.location.href = "/login"
        api.dispatch(logout())
        release()
      }
    } else {
      await authMutex.waitForUnlock()
      result = await baseQuery(args, api, extraOptions)
    }
  }

  return result
}
