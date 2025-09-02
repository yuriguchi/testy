import { createApi } from "@reduxjs/toolkit/dist/query/react"

import { baseQueryWithLogout } from "app/apiSlice"

import { labelInvalidate } from "entities/label/api"

import { suiteInvalidate } from "entities/suite/api"

import { systemStatsInvalidate } from "entities/system/api"

import { testPlanLabelsInvalidate } from "entities/test-plan/api"

import { providesList } from "shared/libs"

import { setDrawerTestCase, setDrawerTestCaseIsArchive } from "../model"

const rootPath = "cases"

export const testCaseApi = createApi({
  reducerPath: "testCaseApi",
  baseQuery: baseQueryWithLogout,
  tagTypes: ["TestCase", "TestCaseHistoryChanges", "TestCaseTestsList"],
  endpoints: (builder) => ({
    searchTestCases: builder.query<SuiteWithCases[], SearchTestCasesQuery>({
      query: (params) => ({
        url: `${rootPath}/search/`,
        params,
      }),
    }),
    createTestCase: builder.mutation<TestCase, TestCaseCreate>({
      query: (body) => ({
        url: `${rootPath}/`,
        method: "POST",
        body,
      }),
      async onQueryStarted(_, { dispatch, queryFulfilled }) {
        await queryFulfilled
        dispatch(labelInvalidate)
        dispatch(testPlanLabelsInvalidate)
        dispatch(suiteInvalidate())
        dispatch(systemStatsInvalidate)
      },
      invalidatesTags: [{ type: "TestCase", id: "LIST" }],
    }),
    deleteTestCase: builder.mutation<void, number>({
      query: (testCaseId) => ({
        url: `${rootPath}/${testCaseId}/`,
        method: "DELETE",
      }),
      async onQueryStarted(_, { dispatch, queryFulfilled }) {
        await queryFulfilled
        dispatch(labelInvalidate)
        dispatch(testPlanLabelsInvalidate)
        dispatch(suiteInvalidate())
        dispatch(systemStatsInvalidate)
      },
      invalidatesTags: [{ type: "TestCase", id: "LIST" }],
    }),
    updateTestCase: builder.mutation<TestCase, TestCaseUpdate>({
      query: (body) => ({
        url: `${rootPath}/${body.id}/`,
        method: "PUT",
        body,
      }),
      async onQueryStarted(args, { queryFulfilled, dispatch }) {
        try {
          const { data } = await queryFulfilled
          dispatch(labelInvalidate)
          dispatch(testPlanLabelsInvalidate)
          dispatch(suiteInvalidate())
          dispatch(setDrawerTestCase(data))
        } catch (error) {
          console.error(error)
        }
      },
      invalidatesTags: (result, _, { id, current_version }) =>
        result
          ? [
              { type: "TestCase", id },
              { type: "TestCase", id: "LIST" },
              { type: "TestCaseHistoryChanges", id: current_version },
            ]
          : [
              { type: "TestCase", id: "LIST" },
              { type: "TestCaseHistoryChanges", id: "LIST" },
            ],
    }),
    archiveTestCase: builder.mutation<void, number>({
      query: (id) => ({
        url: `${rootPath}/${id}/archive/`,
        method: "POST",
      }),
      invalidatesTags: (result, error, id) => [
        { type: "TestCase", id: "LIST" },
        { type: "TestCase", id },
      ],
      async onQueryStarted(args, { queryFulfilled, dispatch }) {
        try {
          await queryFulfilled
          dispatch(setDrawerTestCaseIsArchive(true))
          dispatch(systemStatsInvalidate)
          dispatch(suiteInvalidate())
        } catch (error) {
          console.error(error)
        }
      },
    }),
    getTestCaseById: builder.query<TestCase, GetTestCaseByIdParams>({
      query: ({ testCaseId, ...params }) => ({
        url: `${rootPath}/${testCaseId}/`,
        params,
      }),
      providesTags: (_, __, { testCaseId }) => [{ type: "TestCase", id: testCaseId }],
    }),
    getTestCaseDeletePreview: builder.query<DeletePreviewResponse[], string>({
      query: (id) => ({
        url: `${rootPath}/${id}/delete/preview/`,
      }),
    }),
    getTestCaseArchivePreview: builder.query<DeletePreviewResponse[], string>({
      query: (id) => ({
        url: `${rootPath}/${id}/archive/preview/`,
      }),
    }),
    copyTestCase: builder.mutation<TestCase[], TestCaseCopyBody>({
      query: (body) => ({
        url: `${rootPath}/copy/`,
        method: "POST",
        body,
      }),
      async onQueryStarted(_, { dispatch, queryFulfilled }) {
        await queryFulfilled
        dispatch(labelInvalidate)
        dispatch(testPlanLabelsInvalidate)
        dispatch(suiteInvalidate())
      },
      invalidatesTags: [{ type: "TestCase", id: "LIST" }],
    }),
    getTestCaseHistoryChanges: builder.query<
      PaginationResponse<TestCaseHistoryChange[]>,
      QueryWithPagination<{ testCaseId: number }>
    >({
      query: ({ testCaseId, ...params }) => ({
        url: `${rootPath}/${testCaseId}/history/`,
        params,
      }),
      providesTags: (result) => providesList(result?.results, "TestCaseHistoryChanges", "version"),
    }),
    getTestCaseTestsList: builder.query<
      PaginationResponse<TestsWithPlanBreadcrumbs[]>,
      QueryWithPagination<TestCaseTestsList>
    >({
      query: ({ testCaseId, ...params }) => ({
        url: `${rootPath}/${testCaseId}/tests/`,
        params,
      }),
      providesTags: (result) => providesList(result?.results, "TestCaseTestsList"),
    }),
    restoreTestCase: builder.mutation<TestCase, { testCaseId: number; version: number }>({
      query: ({ testCaseId, ...body }) => ({
        url: `${rootPath}/${testCaseId}/version/restore/`,
        method: "POST",
        body,
      }),
      async onQueryStarted(_, { dispatch, queryFulfilled }) {
        const { data } = await queryFulfilled
        dispatch(labelInvalidate)
        dispatch(testPlanLabelsInvalidate)
        dispatch(suiteInvalidate())
        dispatch(setDrawerTestCase(data))
      },
      invalidatesTags: [{ type: "TestCase", id: "LIST" }],
    }),
    getTestPlanTestCases: builder.query<PaginationResponse<TestCase[]>, SearchTestCasesQuery>({
      query: (params) => ({
        url: `${rootPath}/`,
        params: {
          ...params,
          parent: "null",
        },
      }),
    }),
  }),
})

export const {
  useLazySearchTestCasesQuery,
  useGetTestCaseByIdQuery,
  useLazyGetTestCaseByIdQuery,
  useCreateTestCaseMutation,
  useUpdateTestCaseMutation,
  useArchiveTestCaseMutation,
  useDeleteTestCaseMutation,
  useGetTestCaseDeletePreviewQuery,
  useCopyTestCaseMutation,
  useGetTestCaseHistoryChangesQuery,
  useGetTestCaseTestsListQuery,
  useGetTestCaseArchivePreviewQuery,
  useRestoreTestCaseMutation,
  useGetTestPlanTestCasesQuery,
} = testCaseApi
