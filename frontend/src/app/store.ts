import { Action, ThunkAction, combineReducers, configureStore } from "@reduxjs/toolkit"
import { commentsApi } from "entities/comments/api"
import { customAttributeApi } from "entities/custom-attribute/api"
import { notificationApi } from "entities/notifications/api"
import { notificationWSReducer } from "entities/notifications/model/notification-ws-slice"
import { notificationWSMiddleware } from "entities/notifications/ws"
import { roleApi } from "entities/roles/api"
import { roleReducer } from "entities/roles/model"
import { statusesApi } from "entities/status/api"
import {
  FLUSH,
  PAUSE,
  PERSIST,
  PURGE,
  REGISTER,
  REHYDRATE,
  persistReducer,
  persistStore,
} from "redux-persist"
import storage from "redux-persist/lib/storage"

import { attachmentApi } from "entities/attachment/api"

import { authApi } from "entities/auth/api"
import authReducer from "entities/auth/model"

import { labelApi } from "entities/label/api"

import { parameterApi } from "entities/parameter/api"
import parameterReducer from "entities/parameter/model"

import { projectApi } from "entities/project/api"
import { projectReducer } from "entities/project/model/slice"

import { resultApi } from "entities/result/api"

import { suiteApi } from "entities/suite/api"

import { systemApi } from "entities/system/api"
import { systemReducer } from "entities/system/model/slice"

import { testApi } from "entities/test/api"
import { testReducer, testsfilterReducer } from "entities/test/model"

import { testCaseApi } from "entities/test-case/api"
import { testCaseReducer, testCasesfilterReducer } from "entities/test-case/model"

import { testPlanApi } from "entities/test-plan/api"
import { testPlanReducer } from "entities/test-plan/model"

import { usersApi } from "entities/user/api"
import userReducer from "entities/user/model/user-slice"

import { appReducer } from "./slice"

const persistConfig = {
  key: "root",
  storage,
  whitelist: ["user", "auth", "system"],
}

const rootReducer = combineReducers({
  app: appReducer,
  auth: authReducer,
  testCase: testCaseReducer,
  user: userReducer,
  parameter: parameterReducer,
  project: projectReducer,
  testPlan: testPlanReducer,
  test: testReducer,
  role: roleReducer,
  system: systemReducer,
  testsFilter: testsfilterReducer,
  testCasesFilter: testCasesfilterReducer,
  [systemApi.reducerPath]: systemApi.reducer,
  [authApi.reducerPath]: authApi.reducer,
  [usersApi.reducerPath]: usersApi.reducer,
  [projectApi.reducerPath]: projectApi.reducer,
  [suiteApi.reducerPath]: suiteApi.reducer,
  [testCaseApi.reducerPath]: testCaseApi.reducer,
  [testPlanApi.reducerPath]: testPlanApi.reducer,
  [parameterApi.reducerPath]: parameterApi.reducer,
  [testApi.reducerPath]: testApi.reducer,
  [resultApi.reducerPath]: resultApi.reducer,
  [attachmentApi.reducerPath]: attachmentApi.reducer,
  [labelApi.reducerPath]: labelApi.reducer,
  [statusesApi.reducerPath]: statusesApi.reducer,
  [roleApi.reducerPath]: roleApi.reducer,
  [commentsApi.reducerPath]: commentsApi.reducer,
  [customAttributeApi.reducerPath]: customAttributeApi.reducer,
  [notificationApi.reducerPath]: notificationApi.reducer,
  notificationWS: notificationWSReducer,
})

const persistedReducer = persistReducer(persistConfig, rootReducer)

export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      },
    })
      .concat(authApi.middleware)
      .concat(projectApi.middleware)
      .concat(usersApi.middleware)
      .concat(suiteApi.middleware)
      .concat(testCaseApi.middleware)
      .concat(testPlanApi.middleware)
      .concat(parameterApi.middleware)
      .concat(testApi.middleware)
      .concat(resultApi.middleware)
      .concat(attachmentApi.middleware)
      .concat(labelApi.middleware)
      .concat(statusesApi.middleware)
      .concat(commentsApi.middleware)
      .concat(roleApi.middleware)
      .concat(systemApi.middleware)
      .concat(customAttributeApi.middleware)
      .concat(notificationApi.middleware)
      .concat(notificationWSMiddleware),
  devTools: import.meta.env.NODE_ENV !== "production",
})

export const persistor = persistStore(store)

export type AppDispatch = typeof store.dispatch
export type RootState = ReturnType<typeof store.getState>
export type AppThunk<ReturnType = void> = ThunkAction<
  ReturnType,
  RootState,
  unknown,
  Action<string>
>
