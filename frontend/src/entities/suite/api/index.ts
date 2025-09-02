import { createApi } from "@reduxjs/toolkit/dist/query/react"

import { baseQueryWithLogout } from "app/apiSlice"

import { systemStatsInvalidate } from "entities/system/api"

import { invalidatesList, providesList } from "shared/libs"

const rootPath = "suites"

export const suiteApi = createApi({
  reducerPath: "suiteApi",
  baseQuery: baseQueryWithLogout,
  tagTypes: ["TestSuite", "TestSuiteAncestors", "TestSuiteDeletePreview", "TestSuiteTestCase"],
  endpoints: (builder) => ({
    getTestSuites: builder.query<PaginationResponse<Suite[]>, GetTestSuitesQuery>({
      query: (params) => ({
        url: `${rootPath}/`,
        params,
      }),
      providesTags: (result) => providesList(result?.results, "TestSuite"),
    }),
    getTestSuitesWithTestCases: builder.query<
      PaginationResponse<Suite[] | TestCase[]>,
      GetTestSuitesUnionQuery
    >({
      query: (params) => ({
        url: `${rootPath}/union/`,
        params,
      }),
      providesTags: (result) => providesList(result?.results, "TestSuite"),
    }),
    getTestSuiteAncestors: builder.query<number[], GetAncestors>({
      query: ({ project, id, ...params }) => ({
        url: `${rootPath}/${id}/ancestors/`,
        params: { project, ...params },
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.map((id) => ({
                type: "TestSuiteAncestors" as const,
                id,
              })),
              { type: "TestSuiteAncestors", id: "LIST" },
            ]
          : [{ type: "TestSuiteAncestors", id: "LIST" }],
    }),
    createSuite: builder.mutation<Suite, SuiteCreate>({
      query: (body) => ({
        url: `${rootPath}/`,
        method: "POST",
        body,
      }),
      async onQueryStarted(_, { dispatch, queryFulfilled }) {
        await queryFulfilled
        dispatch(systemStatsInvalidate)
      },
      invalidatesTags: (result) =>
        result?.parent
          ? [
              { type: "TestSuite", id: "LIST" },
              { type: "TestSuiteDeletePreview", id: result?.parent.id },
            ]
          : [
              { type: "TestSuite", id: "LIST" },
              { type: "TestSuiteDeletePreview", id: "LIST" },
            ],
    }),
    updateTestSuite: builder.mutation<SuiteResponseUpdate, { id: Id; body: SuiteUpdate }>({
      query: ({ id, body }) => ({
        url: `${rootPath}/${id}/`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: (result) => invalidatesList(result, "TestSuite"),
    }),
    deleteTestSuite: builder.mutation<void, number>({
      query: (testSuiteId) => ({
        url: `${rootPath}/${testSuiteId}/`,
        method: "DELETE",
      }),
      async onQueryStarted(_, { dispatch, queryFulfilled }) {
        await queryFulfilled
        dispatch(systemStatsInvalidate)
      },
      invalidatesTags: (result) => invalidatesList(result, "TestSuite"),
    }),
    getSuite: builder.query<Suite, GetTestSuiteQuery>({
      query: ({ suiteId, ...params }) => ({
        url: `${rootPath}/${suiteId}/`,
        params,
      }),
      providesTags: (result, error, { suiteId }) => [{ type: "TestSuite", id: suiteId }],
    }),
    getDescendantsTree: builder.query<
      SuiteDescendantsTree[],
      { parent: number | null; project: number }
    >({
      query: (params) => ({
        url: `${rootPath}/descendants-tree/`,
        params,
      }),
    }),
    getSuiteDeletePreview: builder.query<DeletePreviewResponse[], string>({
      query: (id) => ({
        url: `${rootPath}/${id}/delete/preview/`,
      }),
      providesTags: (result, error, id) => [
        { type: "TestSuiteDeletePreview", id },
        { type: "TestSuiteDeletePreview", id: "LIST" },
      ],
    }),
    copySuite: builder.mutation<CopySuiteResponse[], SuiteCopyBody>({
      query: (body) => ({
        url: `${rootPath}/copy/`,
        method: "POST",
        body,
      }),
    }),
    getBreadcrumbs: builder.query<EntityBreadcrumbs, number>({
      query: (id) => ({
        url: `${rootPath}/${id}/breadcrumbs/`,
      }),
    }),
    getSuiteTestCases: builder.query<PaginationResponse<TestCase[]>, GetTestCasesQuery>({
      query: ({ testSuiteId, ...params }) => ({
        url: `${rootPath}/${testSuiteId}/cases/`,
        params,
      }),
      providesTags: (result) => providesList(result?.results, "TestSuiteTestCase"),
    }),
  }),
})

export const suiteInvalidate = (id?: number) => {
  return suiteApi.util.invalidateTags(
    id
      ? [
          { type: "TestSuite", id },
          { type: "TestSuiteDeletePreview", id },
          { type: "TestSuiteTestCase", id },
        ]
      : [
          { type: "TestSuite", id: "LIST" },
          { type: "TestSuiteDeletePreview", id: "LIST" },
          { type: "TestSuiteTestCase", id: "LIST" },
        ]
  )
}

export const {
  useLazyGetTestSuitesQuery,
  useLazyGetSuiteQuery,
  useGetTestSuitesQuery,
  useGetSuiteQuery,
  useGetTestSuiteAncestorsQuery,
  useLazyGetTestSuiteAncestorsQuery,
  useLazyGetTestSuitesWithTestCasesQuery,
  useCreateSuiteMutation,
  useDeleteTestSuiteMutation,
  useUpdateTestSuiteMutation,
  useGetSuiteDeletePreviewQuery,
  useCopySuiteMutation,
  useGetBreadcrumbsQuery,
  useLazyGetDescendantsTreeQuery,
  useGetSuiteTestCasesQuery,
} = suiteApi
