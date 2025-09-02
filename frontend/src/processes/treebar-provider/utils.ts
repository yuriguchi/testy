import { LazyNodeProps, TreeBaseFetcherParams, TreeNodeData } from "shared/libs/tree"

interface BaseNodeEntity {
  id: number
  name: string
  has_children: boolean
}

interface MakeNodeParams extends TreeBaseFetcherParams {
  title?: string
}

// eslint-disable-next-line comma-spacing
export const makeNode = <T extends BaseNodeEntity>(
  data: T[],
  setParams: ((item: T) => MakeNodeParams) | MakeNodeParams,
  additionalProps?: ((item: T) => Partial<LazyNodeProps>) | Partial<LazyNodeProps>
): TreeNodeData<T, LazyNodeProps>[] =>
  data.map((item) => {
    const params = typeof setParams === "function" ? setParams(item) : setParams
    const props = additionalProps
      ? typeof additionalProps === "function"
        ? additionalProps(item)
        : additionalProps
      : undefined

    return {
      id: item.id,
      data: item,
      title: params.title ?? item.name,
      children: [],
      parent: params.parent ?? null,
      props: {
        canOpen: item.has_children,
        isLeaf: !!item.has_children,
        isLoading: false,
        isChecked: false,
        isHalfChecked: false,
        isMoreLoading: false,
        isOpen: false,
        hasMore: false,
        page: params.page,
        level: params.level,
        ...props,
      },
    }
  })
