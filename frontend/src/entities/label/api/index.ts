import { createApi } from "@reduxjs/toolkit/dist/query/react"

import { baseQueryWithLogout } from "app/apiSlice"

import { invalidatesList, providesList } from "shared/libs"

const rootPath = "labels"

export const labelApi = createApi({
  reducerPath: "labelApi",
  baseQuery: baseQueryWithLogout,
  tagTypes: ["Label"],
  endpoints: (builder) => ({
    getLabels: builder.query<Label[], GetLabelsParams>({
      query: (params) => ({
        url: `${rootPath}/`,
        params,
      }),
      providesTags: (result) => providesList(result, "Label"),
    }),
    createLabel: builder.mutation<Label, LabelUpdate>({
      query: (body) => ({
        url: `${rootPath}/`,
        method: "POST",
        body,
      }),
      invalidatesTags: [{ type: "Label", id: "LIST" }],
    }),
    updateLabel: builder.mutation<Label, { id: Id; body: LabelUpdate }>({
      query: ({ id, body }) => ({
        url: `${rootPath}/${id}/`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: (result) => invalidatesList(result, "Label"),
    }),
    deleteLabel: builder.mutation<void, Id>({
      query: (id) => ({
        url: `${rootPath}/${id}/`,
        method: "DELETE",
      }),
      invalidatesTags: [{ type: "Label", id: "LIST" }],
    }),
  }),
})

export const labelInvalidate = labelApi.util.invalidateTags([{ type: "Label", id: "LIST" }])

export const {
  useGetLabelsQuery,
  useCreateLabelMutation,
  useUpdateLabelMutation,
  useDeleteLabelMutation,
} = labelApi
