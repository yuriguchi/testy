import { createApi } from "@reduxjs/toolkit/dist/query/react"

import { baseQueryWithLogout } from "app/apiSlice"

import { testPlanApi } from "entities/test-plan/api"

import { invalidatesList } from "shared/libs"

const rootPath = "tests"

export const testApi = createApi({
  reducerPath: "testApi",
  baseQuery: baseQueryWithLogout,
  tagTypes: ["Test"],
  endpoints: (builder) => ({
    getTest: builder.query<Test, string>({
      query: (testId) => ({
        url: `${rootPath}/${testId}/`,
      }),
      providesTags: (result, error, id) => [{ type: "Test", id }],
    }),
    getTests: builder.query<PaginationResponse<Test[]>, QueryWithPagination<TestGetFilters>>({
      query: (params) => ({
        url: `${rootPath}/`,
        params,
      }),
      providesTags: () => [{ type: "Test", id: "LIST" }],
    }),
    updateTest: builder.mutation<Test, { id: Id; body: TestUpdate }>({
      query: ({ id, body }) => ({
        url: `${rootPath}/${id}/`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: (result) => invalidatesList(result, "Test"),
      async onQueryStarted({ id }, { dispatch, queryFulfilled }) {
        await queryFulfilled
        dispatch(testPlanApi.util.invalidateTags([{ type: "TestPlanTest", id }]))
      },
    }),
    bulkUpdate: builder.mutation<Test[], TestBulkUpdate>({
      query: (body) => ({
        url: `${rootPath}/bulk-update/`,
        method: "PUT",
        body,
      }),
      async onQueryStarted({ current_plan, plan }, { dispatch, queryFulfilled }) {
        await queryFulfilled
        dispatch(
          testPlanApi.util.invalidateTags([{ type: "TestPlanStatistics", id: current_plan }])
        )
        dispatch(
          testPlanApi.util.invalidateTags([
            { type: "TestPlanHistogram", id: current_plan },
            { type: "TestPlanHistogram", id: plan },
          ])
        )
        dispatch(
          testPlanApi.util.invalidateTags([
            { type: "TestPlanLabels", id: "LIST" },
            { type: "TestPlanLabels", id: plan },
          ])
        )
        dispatch(
          testPlanApi.util.invalidateTags([
            { type: "TestPlanCasesIds", id: current_plan },
            { type: "TestPlanCasesIds", id: plan },
          ])
        )

        dispatch(
          testPlanApi.util.invalidateTags([
            { type: "TestPlanTest", id: "LIST" },
            { type: "TestPlanTest", id: current_plan },
          ])
        )
      },
      invalidatesTags: (result) => invalidatesList(result, "Test"),
    }),
  }),
})

export const {
  useGetTestQuery,
  useLazyGetTestsQuery,
  useLazyGetTestQuery,
  useUpdateTestMutation,
  useBulkUpdateMutation,
  useGetTestsQuery,
} = testApi
