import { createApi } from "@reduxjs/toolkit/dist/query/react"

import { baseQueryWithLogout } from "app/apiSlice"

const rootPath = "attachments"

export const attachmentApi = createApi({
  reducerPath: "attachmentApi",
  baseQuery: baseQueryWithLogout,
  endpoints: (builder) => ({
    createAttachment: builder.mutation<IAttachment[], FormData>({
      query: (body) => ({
        url: `${rootPath}/`,
        method: "POST",
        body,
      }),
    }),
  }),
})

export const { useCreateAttachmentMutation } = attachmentApi
