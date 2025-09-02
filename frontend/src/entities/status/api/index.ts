import { createApi } from "@reduxjs/toolkit/dist/query/react"

import { baseQueryWithLogout } from "app/apiSlice"

import { invalidatesList, providesList } from "shared/libs"

const rootPath = "statuses"

export const statusesApi = createApi({
  reducerPath: "statusesApi",
  baseQuery: baseQueryWithLogout,
  tagTypes: ["Status"],
  endpoints: (builder) => ({
    getStatuses: builder.query<Status[], GetStatusesParams>({
      query: ({ project }) => ({
        url: `${rootPath}/`,
        params: { project },
      }),
      providesTags: (result) => providesList(result, "Status"),
    }),
    createStatus: builder.mutation<Status, StatusUpdate>({
      query: (body) => ({
        url: `${rootPath}/`,
        method: "POST",
        body,
      }),
      invalidatesTags: [{ type: "Status", id: "LIST" }],
    }),
    updateStatus: builder.mutation<Status, { id: Id; body: StatusUpdate }>({
      query: ({ id, body }) => ({
        url: `${rootPath}/${id}/`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: (result) => invalidatesList(result, "Status"),
    }),
    deleteStatus: builder.mutation<void, Id>({
      query: (id) => ({
        url: `${rootPath}/${id}/`,
        method: "DELETE",
      }),
      invalidatesTags: [{ type: "Status", id: "LIST" }],
    }),
  }),
})

export const statusInvalidate = statusesApi.util.invalidateTags([{ type: "Status", id: "LIST" }])

export const {
  useGetStatusesQuery,
  useLazyGetStatusesQuery,
  useCreateStatusMutation,
  useUpdateStatusMutation,
  useDeleteStatusMutation,
} = statusesApi
