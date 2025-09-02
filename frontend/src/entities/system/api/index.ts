import { createApi } from "@reduxjs/toolkit/dist/query/react"

import { baseQueryWithLogout } from "app/apiSlice"

import { providesList } from "shared/libs"

const rootPath = "system"

export const systemApi = createApi({
  reducerPath: "systemApi",
  baseQuery: baseQueryWithLogout,
  tagTypes: ["SystemMessages", "SystemStatistic"],
  endpoints: (builder) => ({
    getSystemMessages: builder.query<SystemMessage[], void>({
      query: () => `${rootPath}/messages/`,
      providesTags: (result) => providesList(result, "SystemMessages"),
    }),
    getSystemStats: builder.query<SystemStatistic, void>({
      query: () => `${rootPath}/statistics/`,
      providesTags: [{ type: "SystemStatistic", id: "LIST" }],
    }),
  }),
})

export const systemStatsInvalidate = systemApi.util.invalidateTags([
  { type: "SystemStatistic", id: "LIST" },
])

export const { useGetSystemMessagesQuery, useGetSystemStatsQuery } = systemApi
