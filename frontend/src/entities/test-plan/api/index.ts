import { createApi } from "@reduxjs/toolkit/dist/query/react"

import { baseQueryWithLogout } from "app/apiSlice"

import { labelInvalidate } from "entities/label/api"

import { systemStatsInvalidate } from "entities/system/api"

import { testApi } from "entities/test/api"

import { invalidatesList, providesList } from "shared/libs"

const rootPath = "testplans"

export const testPlanApi = createApi({
  reducerPath: "testPlanApi",
  baseQuery: baseQueryWithLogout,
  tagTypes: [
    "TestPlan",
    "TestPlanTest",
    "TestPlanAncestors",
    "TestPlanStatistics",
    "TestPlanLabels",
    "TestPlanCasesIds",
    "TestPlanHistogram",
    "TestPlanStatuses",
  ],
  endpoints: (builder) => ({
    getTestPlans: builder.query<
      PaginationResponse<TestPlan[]>,
      QueryWithPagination<TestPlansQuery>
    >({
      query: (params) => ({
        url: `${rootPath}/`,
        params,
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.results.map(({ id }) => ({
                type: "TestPlan" as const,
                id,
              })),
              { type: "TestPlan", id: "LIST" },
            ]
          : [{ type: "TestPlan", id: "LIST" }],
    }),
    getTestPlansWithTests: builder.query<
      PaginationResponse<TestPlan[] | Test[]>,
      QueryWithPagination<TestPlansUnionQuery>
    >({
      query: (params) => ({
        url: `${rootPath}/union/`,
        params,
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.results.map(({ id }) => ({
                type: "TestPlan" as const,
                id,
              })),
              { type: "TestPlan", id: "LIST" },
            ]
          : [{ type: "TestPlan", id: "LIST" }],
    }),
    getTestPlanAncestors: builder.query<number[], GetAncestors>({
      query: ({ project, id, ...params }) => ({
        url: `${rootPath}/${id}/ancestors/`,
        params: {
          project,
          ...params,
        },
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.map((id) => ({
                type: "TestPlanAncestors" as const,
                id,
              })),
              { type: "TestPlanAncestors", id: "LIST" },
            ]
          : [{ type: "TestPlanAncestors", id: "LIST" }],
    }),
    getTestPlan: builder.query<TestPlan, TestPlanQuery>({
      query: ({ testPlanId, ...params }) => ({
        url: `${rootPath}/${testPlanId}/`,
        params,
      }),
      providesTags: (result, error, { testPlanId }) => [
        { type: "TestPlan", id: String(testPlanId) },
      ],
    }),
    getTestPlanActivity: builder.query<
      PaginationResponse<Record<string, TestPlanActivityResult[]>>,
      TestPlanActivityParams
    >({
      query: ({ testPlanId, ...params }) => ({
        url: `${rootPath}/${testPlanId}/activity/`,
        params,
      }),
      providesTags: (result, error, { testPlanId: id }) => [{ type: "TestPlan", id }],
    }),
    deleteTestPlan: builder.mutation<void, number>({
      query: (testPlanId) => ({
        url: `${rootPath}/${testPlanId}/`,
        method: "DELETE",
      }),
      async onQueryStarted(_, { dispatch, queryFulfilled }) {
        await queryFulfilled
        dispatch(systemStatsInvalidate)
      },
      invalidatesTags: [{ type: "TestPlan", id: "LIST" }],
    }),
    archiveTestPlan: builder.mutation<void, number>({
      query: (testPlanId) => ({
        url: `${rootPath}/${testPlanId}/archive/`,
        method: "POST",
      }),
      async onQueryStarted(_, { dispatch, queryFulfilled }) {
        await queryFulfilled
        dispatch(systemStatsInvalidate)
      },
      invalidatesTags: (result, error, id) => [
        { type: "TestPlan", id: "LIST" },
        { type: "TestPlan", id },
      ],
    }),
    createTestPlan: builder.mutation<TestPlan[], TestPlanCreate>({
      query: (body) => ({
        url: `${rootPath}/`,
        method: "POST",
        body,
      }),
      async onQueryStarted(_, { dispatch, queryFulfilled }) {
        await queryFulfilled
        dispatch(systemStatsInvalidate)
      },
      invalidatesTags: (result) => invalidatesList(result?.[0], "TestPlan"),
    }),
    updateTestPlan: builder.mutation<TestPlan, { id: Id; body: TestPlanUpdate }>({
      query: ({ id, body }) => ({
        url: `${rootPath}/${id}/`,
        method: "PATCH",
        body,
        redirect: "manual",
      }),
      async onQueryStarted({ id }, { dispatch, queryFulfilled }) {
        await queryFulfilled
        dispatch(
          testPlanApi.util.invalidateTags([
            { type: "TestPlanTest", id },
            { type: "TestPlanTest", id: "LIST" },
          ])
        )
        dispatch(testPlanApi.util.invalidateTags([{ type: "TestPlanStatistics", id }]))
        dispatch(testPlanApi.util.invalidateTags([{ type: "TestPlanHistogram", id }]))
        dispatch(testPlanApi.util.invalidateTags([{ type: "TestPlanLabels", id: "LIST" }]))
        dispatch(testPlanApi.util.invalidateTags([{ type: "TestPlanCasesIds", id }]))
        dispatch(testApi.util.invalidateTags([{ type: "Test", id: "LIST" }]))
        dispatch(labelInvalidate)
        dispatch(systemStatsInvalidate)
      },
      invalidatesTags: (result) => invalidatesList(result, "TestPlan"),
    }),
    getTestPlanStatistics: builder.query<TestPlanStatistics[], TestPlanStatisticsParams>({
      query: (params) => ({
        url: `${rootPath}/statistics/`,
        params,
      }),
      providesTags: (result, error, { project, parent }) => [
        { type: "TestPlanStatistics", id: `${project}-${parent}` },
      ],
    }),
    getTestPlanHistogram: builder.query<TestPlanHistogramData[], TestPlanHistogramParams>({
      query: (params) => ({
        url: `${rootPath}/histogram/`,
        params,
      }),
      providesTags: (result, error, { project, parent }) => [
        { type: "TestPlanHistogram", id: `${project}-${parent}` },
      ],
    }),
    getTestPlanLabels: builder.query<Label[], GetTestPlanLabelsParams>({
      query: (params) => ({
        url: `${rootPath}/labels/`,
        params,
      }),
      providesTags: () => [{ type: "TestPlanLabels", id: "LIST" }],
    }),
    getTestPlanTests: builder.query<
      PaginationResponse<Test[]>,
      QueryWithPagination<TestGetFilters>
    >({
      query: ({ testPlanId, ...params }) => ({
        url: `${rootPath}/${testPlanId}/tests/`,
        params,
      }),
      providesTags: (result) => providesList(result?.results, "TestPlanTest"),
    }),
    getTestPlanSuites: builder.query<TestPlanSuite[], { parent: number | null; project: number }>({
      query: (params) => ({
        url: `${rootPath}/suites/`,
        params: {
          show_descendants: true,
          ...params,
        },
      }),
    }),
    getDescendantsTree: builder.query<
      TestPlanDescendantsTree[],
      { parent: number | null; project: number }
    >({
      query: (params) => ({
        url: `${rootPath}/descendants-tree/`,
        params,
      }),
    }),
    getTestPlanCases: builder.query<{ case_ids: string[] }, TestPlanCasesParams>({
      query: ({ testPlanId, include_children = false }) => ({
        url: `${rootPath}/${testPlanId}/cases/`,
        params: {
          include_children,
        },
      }),
      providesTags: (result, error, { testPlanId }) => [
        { type: "TestPlanCasesIds", id: testPlanId },
      ],
    }),
    getTestPlanDeletePreview: builder.query<DeletePreviewResponse[], string>({
      query: (testPlanId) => ({
        url: `${rootPath}/${testPlanId}/delete/preview/`,
      }),
      providesTags: (result, error, id) => [{ type: "TestPlan", id }],
    }),
    getTestPlanArchivePreview: builder.query<DeletePreviewResponse[], string>({
      query: (testPlanId) => ({
        url: `${rootPath}/${testPlanId}/archive/preview/`,
      }),
      providesTags: (result, error, id) => [{ type: "TestPlan", id }],
    }),
    сopyTestPlan: builder.mutation<TestPlan[], TestPlanCopyBody>({
      query: (body) => ({
        url: `${rootPath}/copy/`,
        method: "POST",
        body,
      }),
      async onQueryStarted(_, { dispatch, queryFulfilled }) {
        await queryFulfilled
        dispatch(systemStatsInvalidate)
      },
      invalidatesTags: [{ type: "TestPlan", id: "LIST" }],
    }),
    getTestPlanStatuses: builder.query<Status[], string | number>({
      query: (testPlanId) => `${rootPath}/${testPlanId}/statuses/`,
      providesTags: (result, error, id) => [{ type: "TestPlanStatuses", id }],
    }),
    getTestPlanActivityStatuses: builder.query<Status[], string | number>({
      query: (testPlanId) => `${rootPath}/${testPlanId}/activity/statuses/`,
      providesTags: (result, error, id) => [{ type: "TestPlanStatuses", id }],
    }),
    getBreadcrumbs: builder.query<EntityBreadcrumbs, number>({
      query: (id) => ({
        url: `${rootPath}/${id}/breadcrumbs/`,
      }),
    }),
  }),
})

export const testPlanInvalidate = (id?: number) => {
  return testPlanApi.util.invalidateTags(
    id ? [{ type: "TestPlan", id }] : [{ type: "TestPlan", id: "LIST" }]
  )
}

export const testPlanLabelsInvalidate = testPlanApi.util.invalidateTags([
  { type: "TestPlanLabels", id: "LIST" },
])

export const testPlanStatusesInvalidate = (id: string | number) =>
  testPlanApi.util.invalidateTags([{ type: "TestPlanStatuses", id }])

export const {
  useGetTestPlanQuery,
  useLazyGetTestPlanQuery,
  useLazyGetTestPlansQuery,
  useLazyGetTestPlansWithTestsQuery,
  useGetTestPlanAncestorsQuery,
  useLazyGetTestPlanAncestorsQuery,
  useCreateTestPlanMutation,
  useDeleteTestPlanMutation,
  useGetTestPlanStatisticsQuery,
  useUpdateTestPlanMutation,
  useLazyGetTestPlanSuitesQuery,
  useGetTestPlanLabelsQuery,
  useLazyGetTestPlanActivityQuery,
  useGetTestPlanCasesQuery,
  useGetTestPlanDeletePreviewQuery,
  useGetTestPlanArchivePreviewQuery,
  useArchiveTestPlanMutation,
  useGetTestPlanHistogramQuery,
  useСopyTestPlanMutation,
  useLazyGetTestPlanActivityStatusesQuery,
  useLazyGetTestPlanStatusesQuery,
  useGetBreadcrumbsQuery,
  useGetTestPlanTestsQuery,
  useLazyGetDescendantsTreeQuery,
} = testPlanApi
