import { createApi } from "@reduxjs/toolkit/dist/query/react"

import { baseQueryWithLogout } from "app/apiSlice"

import { setUser } from "entities/auth/model"

import { invalidatesList } from "shared/libs"

const rootPath = "users"

export const usersApi = createApi({
  reducerPath: "usersApi",
  tagTypes: ["User", "Profile", "Config"],
  baseQuery: baseQueryWithLogout,
  endpoints: (builder) => ({
    getConfig: builder.query<UserConfig, unknown>({
      query: () => `${rootPath}/me/config/`,
      providesTags: () => ["Config"],
    }),
    updateConfig: builder.mutation<void, UserConfig>({
      query: (body) => ({
        url: `${rootPath}/me/config/`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: ["Config"],
    }),
    getUsers: builder.query<PaginationResponse<User[]>, QueryWithPagination<GetUsersQuery>>({
      query: (params) => ({
        url: `${rootPath}/`,
        params,
      }),
      providesTags: () => [{ type: "User", id: "LIST" }],
    }),
    getUserById: builder.query<User, number>({
      query: (id) => ({
        url: `${rootPath}/${id}/`,
      }),
      providesTags: (res, err, id) => [{ type: "User", id }],
    }),
    getMe: builder.query<User, void>({
      query: () => `${rootPath}/me/`,
      providesTags: () => [{ type: "Profile" }],
      async onQueryStarted(_, { dispatch, queryFulfilled }) {
        try {
          const { data } = await queryFulfilled
          dispatch(setUser(data))
        } catch (error) {
          console.error(error)
        }
      },
    }),
    updateMe: builder.mutation<void, UserUpdate>({
      query: (body) => ({
        url: `${rootPath}/me/`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: [{ type: "Profile" }],
    }),
    updatePassword: builder.mutation<void, { password: string }>({
      query: (body) => ({
        url: `${rootPath}/change-password/`,
        method: "POST",
        body,
      }),
      invalidatesTags: [{ type: "Profile" }],
    }),
    createUser: builder.mutation<User, UserCreate>({
      query: (body) => ({
        url: `${rootPath}/`,
        method: "POST",
        body,
      }),
      invalidatesTags: [{ type: "User", id: "LIST" }],
    }),
    updateUser: builder.mutation<User, { id: Id; body: UserUpdate }>({
      query: ({ id, body }) => ({
        url: `${rootPath}/${id}/`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: (result) => invalidatesList(result, "User"),
    }),
    deleteUser: builder.mutation<void, number>({
      query: (id) => ({
        url: `${rootPath}/${id}/`,
        method: "DELETE",
      }),
      invalidatesTags: [{ type: "User", id: "LIST" }],
    }),
    uploadAvatar: builder.mutation<IAttachment[], FormData>({
      query: (body) => ({
        url: `${rootPath}/me/avatar/`,
        method: "POST",
        body,
      }),
      invalidatesTags: [{ type: "Profile" }],
    }),
    deleteAvatar: builder.mutation<void, void>({
      query: () => ({
        url: `${rootPath}/me/avatar/`,
        method: "DELETE",
      }),
      invalidatesTags: [{ type: "Profile" }],
    }),
  }),
})

export const {
  useGetUsersQuery,
  useLazyGetUserByIdQuery,
  useLazyGetUsersQuery,
  useCreateUserMutation,
  useUpdateUserMutation,
  useDeleteUserMutation,
  useGetMeQuery,
  useLazyGetMeQuery,
  useGetConfigQuery,
  useLazyGetConfigQuery,
  useUpdateMeMutation,
  useUpdatePasswordMutation,
  useUpdateConfigMutation,
  useUploadAvatarMutation,
  useDeleteAvatarMutation,
} = usersApi
