import { createApi } from "@reduxjs/toolkit/dist/query/react"

import { baseQueryWithLogout } from "app/apiSlice"

import { invalidatesList, providesList } from "shared/libs"

const rootPath = "parameters"

export const parameterApi = createApi({
  reducerPath: "parameterApi",
  baseQuery: baseQueryWithLogout,
  tagTypes: ["Parameter"],
  endpoints: (builder) => ({
    getParameters: builder.query<IParameter[], Id>({
      query: (projectId) => ({
        url: `${rootPath}/`,
        params: { project: projectId, treeview: true },
      }),
      providesTags: (result) => providesList(result, "Parameter"),
    }),
    createParameter: builder.mutation<IParameter, IParameterUpdate>({
      query: (body) => ({
        url: `${rootPath}/`,
        method: "POST",
        body,
      }),
      invalidatesTags: [{ type: "Parameter", id: "LIST" }],
    }),
    updateParameter: builder.mutation<IParameter, { id: Id; body: IParameterUpdate }>({
      query: ({ id, body }) => ({
        url: `${rootPath}/${id}/`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: (result) => invalidatesList(result, "Parameter"),
    }),
    deleteParameter: builder.mutation<void, Id>({
      query: (id) => ({
        url: `${rootPath}/${id}/`,
        method: "DELETE",
      }),
      invalidatesTags: [{ type: "Parameter", id: "LIST" }],
    }),
  }),
})

export const {
  useGetParametersQuery,
  useCreateParameterMutation,
  useUpdateParameterMutation,
  useDeleteParameterMutation,
} = parameterApi
