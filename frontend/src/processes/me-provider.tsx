import { PropsWithChildren, createContext, useMemo } from "react"

import { useAppDispatch, useAppSelector } from "app/hooks"

import { useGetConfigQuery, useGetMeQuery, useUpdateConfigMutation } from "entities/user/api"
import { selectUserConfig, setUserConfig } from "entities/user/model"

interface MeContextType {
  me: User | null
  userConfig: UserConfig | null
  updateConfig: (data: object) => Promise<void>
  isLoading: boolean
}

export const MeContext = createContext<MeContextType>({
  me: null,
  userConfig: null,
  updateConfig: async () => {},
  isLoading: false,
})

export const MeProvider = ({ children }: PropsWithChildren) => {
  const { data: me, isLoading: isMeLoading } = useGetMeQuery()
  const { data: config, isLoading: isConfigLoading } = useGetConfigQuery({}, { skip: !me })
  const [updateConfigMutation] = useUpdateConfigMutation()

  const dispatch = useAppDispatch()
  const userConfigState = useAppSelector(selectUserConfig)

  const updateConfig = async (data: object) => {
    const newConfig = {
      ...userConfigState,
      ...data,
    }

    dispatch(setUserConfig(newConfig))
    await updateConfigMutation(newConfig)
  }

  const userConfig = useMemo(() => {
    if (!config) {
      return null
    }

    return {
      ...config,
      ...userConfigState,
    }
  }, [config, userConfigState])

  const value: MeContextType | null = useMemo(() => {
    if (!me || !userConfig) {
      return null
    }

    return {
      me,
      userConfig,
      updateConfig,
      isLoading: isMeLoading || isConfigLoading,
    }
  }, [me, userConfig, updateConfig, isMeLoading, isConfigLoading])

  if (!value) {
    return null
  }

  return <MeContext.Provider value={value}>{children}</MeContext.Provider>
}
