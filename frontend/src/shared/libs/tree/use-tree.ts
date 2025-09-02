import { useMemo, useReducer } from "react"

import { TreeApi } from "./api"
import { BaseTreeNodeProps, TreeNodeData } from "./api/types"

interface Props<TData, TProps> {
  initData?: TreeNodeData<TData, TProps>[]
}

export const useTree = <TData, TProps extends BaseTreeNodeProps>({
  initData,
}: Props<TData, TProps>): TreeApi<TData, TProps> => {
  const [, forceRerender] = useReducer((x: number) => x + 1, 0)

  const api = useMemo(() => {
    return new TreeApi(initData ?? [], forceRerender)
  }, [])

  return api
}
