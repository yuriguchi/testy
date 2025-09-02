import {
  BaseQueryFn,
  FetchArgs,
  FetchBaseQueryError,
  createApi,
} from "@reduxjs/toolkit/dist/query/react"

import { authMutex, authQuery } from "app/apiSlice"
import { handleError } from "app/slice"

import { logout } from "../model"

export const getCsrfCookie = () => {
  const cookies = document.cookie.split(";")
  let csrfToken = ""

  cookies.forEach((cookie) => {
    if (cookie.trim().startsWith("csrftoken=")) {
      csrfToken = cookie.split("=")[1]
    }
  })

  return csrfToken
}

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

export const authApi = createApi({
  reducerPath: "authApi",
  baseQuery: baseQueryAuth,
  endpoints: (builder) => ({
    login: builder.mutation<void, { password: string; username: string; remember_me: boolean }>({
      query: (credentials) => ({
        url: "login/",
        method: "POST",
        body: { ...credentials },
      }),
      async onQueryStarted(args, { queryFulfilled }) {
        try {
          await queryFulfilled
        } catch (error) {
          console.error(error)
        }
      },
    }),
    logout: builder.mutation<void, void>({
      query: () => ({
        url: "logout/",
        method: "POST",
        headers: { "X-CSRFToken": getCsrfCookie() },
        body: {},
      }),
      async onQueryStarted(args, { dispatch, queryFulfilled }) {
        try {
          await queryFulfilled

          dispatch(logout())
        } catch (error) {
          console.error(error)
          dispatch(logout())
        }
      },
    }),
  }),
})

export const { useLoginMutation, useLogoutMutation } = authApi
