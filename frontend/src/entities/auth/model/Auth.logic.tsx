import { FetchBaseQueryError } from "@reduxjs/toolkit/dist/query"
import { useState } from "react"
import { SubmitHandler, useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"

import { persistor } from "app/store"

import { useLoginMutation } from "entities/auth/api"

import { useLazyGetConfigQuery, useLazyGetMeQuery } from "entities/user/api"

import { clearPrevPageUrl, getPrevPageUrl } from "shared/libs"

export interface Inputs {
  username: string
  password: string
  remember_me: boolean
}

interface LocationState {
  from?: {
    pathname: string
    search: string
  }
}

export const useAuthLogic = () => {
  const { t } = useTranslation()
  const [login] = useLoginMutation()
  const [getMe] = useLazyGetMeQuery()
  const [getUserConfig] = useLazyGetConfigQuery()
  const [errMsg, setErrMsg] = useState("")
  const navigate = useNavigate()
  const { handleSubmit, reset, control } = useForm<Inputs>({
    defaultValues: {
      username: "",
      password: "",
      remember_me: false,
    },
  })
  const locationState = useLocation().state as LocationState
  const [isLoading, setIsLoading] = useState(false)

  const onSubmit: SubmitHandler<Inputs> = async (data) => {
    setErrMsg("")
    setIsLoading(true)

    try {
      await persistor.purge()
      await login(data).unwrap()
      await getMe().unwrap()
      await getUserConfig({}).unwrap()
      reset()

      const prevPageUrl = getPrevPageUrl()
      if (prevPageUrl) {
        clearPrevPageUrl()
        navigate(prevPageUrl, { replace: true })
        return
      }

      if (locationState?.from) {
        // django plugin redirect
        if (locationState.from.search.includes("?next=/plugins/")) {
          const path = locationState.from.search.replace("?next=/", "")
          window.location.replace(`${locationState.from.pathname}${path}`)
          return
        }

        navigate(`${locationState.from.pathname}${locationState.from.search}`)
        return
      }

      navigate("/")
    } catch (err: unknown) {
      const error = err as FetchBaseQueryError

      if (!error?.status) {
        setErrMsg(t("No Server Response"))
      } else if (error.status === 400) {
        setErrMsg(t("Missing Username or Password"))
      } else if (error.status === 401) {
        setErrMsg(t("Unauthorized"))
      } else {
        setErrMsg(t("Login Failed"))
      }
    }
    setIsLoading(false)
  }

  return {
    onSubmit: handleSubmit(onSubmit),
    errMsg,
    control,
    isLoading,
  }
}
