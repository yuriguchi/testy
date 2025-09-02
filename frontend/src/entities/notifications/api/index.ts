import { createApi } from "@reduxjs/toolkit/dist/query/react"

import { baseQueryWithLogout } from "app/apiSlice"

import { providesList } from "shared/libs"

const rootPath = "notifications"

export const notificationApi = createApi({
  reducerPath: "notificationApi",
  baseQuery: baseQueryWithLogout,
  tagTypes: ["Notification", "NotificationSettings"],
  endpoints: (builder) => ({
    getNotificationSettings: builder.query<NotificationSetting[], void>({
      query: () => `${rootPath}/settings/`,
      providesTags: (result) => providesList(result, "NotificationSettings"),
    }),
    enableNotification: builder.mutation<void, { settings: number[] }>({
      query: ({ settings }) => ({
        url: `${rootPath}/enable/`,
        method: "POST",
        body: { settings },
      }),
      invalidatesTags: ["NotificationSettings"],
    }),
    disableNotification: builder.mutation<void, { settings: number[] }>({
      query: ({ settings }) => ({
        url: `${rootPath}/disable/`,
        method: "POST",
        body: { settings },
      }),
      invalidatesTags: ["NotificationSettings"],
    }),
    getNotificationsList: builder.query<
      PaginationResponse<NotificationData[]>,
      QueryWithPagination<GetNotificationQuery>
    >({
      query: (params) => ({
        url: `${rootPath}/`,
        params,
      }),
      providesTags: () => [{ type: "Notification", id: "LIST" }],
    }),
    markAs: builder.mutation<void, MarkAsMutation>({
      query: (body) => ({
        url: `${rootPath}/mark-as/`,
        method: "POST",
        body: {
          ...body,
        },
      }),
      invalidatesTags: () => [{ type: "Notification", id: "LIST" }],
    }),
  }),
})

export const {
  useGetNotificationSettingsQuery,
  useEnableNotificationMutation,
  useDisableNotificationMutation,
  useGetNotificationsListQuery,
  useLazyGetNotificationsListQuery,
  useMarkAsMutation,
} = notificationApi
