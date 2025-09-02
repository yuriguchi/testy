import { createApi } from "@reduxjs/toolkit/dist/query/react"

import { baseQueryWithLogout } from "app/apiSlice"

import { invalidatesList, providesList } from "shared/libs"

const rootPath = "custom-attributes"

export const customAttributeApi = createApi({
  reducerPath: "customAttributeApi",
  baseQuery: baseQueryWithLogout,
  tagTypes: ["CustomAttribute"],
  endpoints: (builder) => ({
    getCustomAttributes: builder.query<CustomAttribute[], GetCustomAttributesParams>({
      query: (params) => ({
        url: `${rootPath}/`,
        params,
      }),
      providesTags: (result) => providesList(result, "CustomAttribute"),
    }),
    createCustomAttribute: builder.mutation<CustomAttribute, CustomAttributeUpdate>({
      query: (body) => ({
        url: `${rootPath}/`,
        method: "POST",
        body,
      }),
      invalidatesTags: (result) => invalidatesList(result, "CustomAttribute"),
    }),
    updateCustomAttribute: builder.mutation<
      CustomAttribute,
      { id: Id; body: CustomAttributeUpdate }
    >({
      query: ({ id, body }) => ({
        url: `${rootPath}/${id}/`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: (result) => invalidatesList(result, "CustomAttribute"),
    }),
    deleteCustomAttribute: builder.mutation<void, Id>({
      query: (id) => ({
        url: `${rootPath}/${id}/`,
        method: "DELETE",
      }),
      invalidatesTags: (result) => invalidatesList(result, "CustomAttribute"),
    }),
    getCustomAttributeContentTypes: builder.query<CustomAttributeContentType[], void>({
      query: () => ({ url: `${rootPath}/content-types/` }),
    }),
  }),
})

export const {
  useGetCustomAttributesQuery,
  useCreateCustomAttributeMutation,
  useUpdateCustomAttributeMutation,
  useDeleteCustomAttributeMutation,
  useGetCustomAttributeContentTypesQuery,
} = customAttributeApi
