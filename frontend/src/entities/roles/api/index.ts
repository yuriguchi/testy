import { createApi } from "@reduxjs/toolkit/dist/query/react"

import { baseQueryWithLogout } from "app/apiSlice"

import { invalidatesList } from "shared/libs"

const rootPath = "roles"

export const roleApi = createApi({
  reducerPath: "roleApi",
  baseQuery: baseQueryWithLogout,
  tagTypes: ["Role", "User"],
  endpoints: (builder) => ({
    getRoles: builder.query<PaginationResponse<Role[]>, PaginationQuery>({
      query: () => ({
        url: `${rootPath}/`,
      }),
      providesTags: () => [{ type: "Role", id: "LIST" }],
    }),
    getRole: builder.query<Role, number>({
      query: (roleId) => `${rootPath}/${roleId}/`,
      providesTags: (result, error, id) => [{ type: "Role", id }],
    }),
    createRole: builder.mutation<Role, RoleUpdate>({
      query: (body: RoleUpdate) => ({
        url: `${rootPath}/`,
        method: "POST",
        body,
      }),
      invalidatesTags: [{ type: "Role", id: "LIST" }],
    }),
    updateRole: builder.mutation<Role, { id: Id; body: RoleUpdate }>({
      query: ({ id, body }) => ({
        url: `${rootPath}/${id}/`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: (result) => invalidatesList(result, "Role"),
    }),
    deleteRole: builder.mutation<void, Id>({
      query: (id) => ({
        url: `${rootPath}/${id}/`,
        method: "DELETE",
      }),
      invalidatesTags: [{ type: "Role", id: "LIST" }],
    }),
    assignRole: builder.mutation<void, AssignRole>({
      query: (body) => ({
        url: `${rootPath}/assign/`,
        method: "POST",
        body,
      }),
      invalidatesTags: [{ type: "User", id: "LIST" }],
    }),
    unassignRole: builder.mutation<void, UnassignRole>({
      query: (body) => ({
        url: `${rootPath}/unassign/`,
        method: "POST",
        body,
      }),
      invalidatesTags: [{ type: "User", id: "LIST" }],
    }),
    updateAssignedRole: builder.mutation<void, AssignRole>({
      query: (body) => ({
        url: `${rootPath}/assign/`,
        method: "PUT",
        body,
      }),
      invalidatesTags: [{ type: "User", id: "LIST" }],
    }),
    getPermissions: builder.query<PaginationResponse<Permission[]>, PaginationQuery>({
      query: () => ({
        url: `${rootPath}/permissions/`,
      }),
    }),
  }),
})

export const roleInvalidate = roleApi.util.invalidateTags([{ type: "Role", id: "LIST" }])

export const {
  useGetRolesQuery,
  useCreateRoleMutation,
  useUpdateRoleMutation,
  useDeleteRoleMutation,
  useGetPermissionsQuery,
  useAssignRoleMutation,
  useUnassignRoleMutation,
  useUpdateAssignedRoleMutation,
} = roleApi
