import { createApi } from "@reduxjs/toolkit/dist/query/react"

import { baseQueryWithLogout } from "app/apiSlice"

import { systemStatsInvalidate } from "entities/system/api"

import { testPlanInvalidate } from "entities/test-plan/api"

import { invalidatesList } from "shared/libs"

const rootPath = "projects"

export const projectApi = createApi({
  reducerPath: "projectApi",
  tagTypes: ["Project"],
  baseQuery: baseQueryWithLogout,
  endpoints: (builder) => ({
    getProjects: builder.query<
      PaginationResponse<Project[]>,
      QueryWithPagination<GetProjectsQuery>
    >({
      query: ({ favorites = false, ...params }) => ({
        url: `${rootPath}/`,
        params: {
          favorites,
          ...params,
        },
      }),
      providesTags: () => [{ type: "Project", id: "LIST" }],
    }),
    getProject: builder.query<Project, number>({
      query: (projectId) => `${rootPath}/${projectId}/`,
      providesTags: (result, error, id) => [{ type: "Project", id }],
    }),
    createProject: builder.mutation<Project, FormData>({
      query: (body) => ({
        url: `${rootPath}/`,
        method: "POST",
        body,
      }),
      async onQueryStarted(_, { dispatch, queryFulfilled }) {
        await queryFulfilled
        dispatch(systemStatsInvalidate)
      },
      invalidatesTags: [{ type: "Project", id: "LIST" }],
    }),
    updateProject: builder.mutation<Project, { id: Id; body: FormData }>({
      query: ({ id, body }) => ({
        url: `${rootPath}/${id}/`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: (result) => invalidatesList(result, "Project"),
    }),
    updateProjectJson: builder.mutation<Project, { id: Id; body: Partial<Project> }>({
      query: ({ id, body }) => ({
        url: `${rootPath}/${id}/`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: (result) => invalidatesList(result, "Project"),
    }),
    deleteProject: builder.mutation<void, number>({
      query: (id) => ({
        url: `${rootPath}/${id}/`,
        method: "DELETE",
      }),
      async onQueryStarted(_, { dispatch, queryFulfilled }) {
        await queryFulfilled
        dispatch(systemStatsInvalidate)
      },
      invalidatesTags: [{ type: "Project", id: "LIST" }],
    }),
    archiveProject: builder.mutation<void, number>({
      query: (id) => ({
        url: `${rootPath}/${id}/archive/`,
        method: "POST",
      }),
      async onQueryStarted(_, { dispatch, queryFulfilled }) {
        await queryFulfilled
        dispatch(systemStatsInvalidate)
        dispatch(testPlanInvalidate())
      },
      invalidatesTags: (result, error, id) => [
        { type: "Project", id: Number(id) },
        { type: "Project", id: "LIST" },
      ],
    }),
    getProjectDeletePreview: builder.query<DeletePreviewResponse[], string>({
      query: (id) => ({
        url: `${rootPath}/${id}/delete/preview/`,
      }),
    }),
    getProjectArchivePreview: builder.query<DeletePreviewResponse[], string>({
      query: (id) => ({
        url: `${rootPath}/${id}/archive/preview/`,
      }),
      providesTags: (result, error, id) => [{ type: "Project", id }],
    }),
    getProjectProgress: builder.query<ProjectsProgress[], ProjectProgressParams>({
      query: ({ projectId, period_date_end, period_date_start }) => ({
        url: `${rootPath}/${projectId}/progress/`,
        method: "GET",
        params: { end_date: period_date_end, start_date: period_date_start },
      }),
      providesTags: (result, error, { projectId }) => [{ type: "Project", id: projectId }],
    }),
    getMembers: builder.query<
      PaginationResponse<UserWithRoles[]>,
      QueryWithPagination<GetUsersQuery>
    >({
      query: ({ id, ...rest }) => ({
        url: `${rootPath}/${id}/members/`,
        params: rest,
      }),
    }),
    requestAccess: builder.mutation<void, { id: number; reason?: string }>({
      query: ({ id, reason }) => ({
        url: `${rootPath}/${id}/access/`,
        method: "POST",
        body: {
          reason,
        },
      }),
    }),
  }),
})

export const {
  useGetProjectsQuery,
  useGetProjectQuery,
  useLazyGetProjectsQuery,
  useCreateProjectMutation,
  useUpdateProjectMutation,
  useUpdateProjectJsonMutation,
  useDeleteProjectMutation,
  useLazyGetProjectProgressQuery,
  useGetProjectDeletePreviewQuery,
  useArchiveProjectMutation,
  useGetProjectArchivePreviewQuery,
  useGetMembersQuery,
  useRequestAccessMutation,
} = projectApi
