import { LazyNodeProps, LazyTreeApi } from "shared/libs/tree"

export interface TreeSettings {
  collapsed: boolean
  show_archived: boolean
  plans: {
    sortBy: "asc" | "desc"
    filterBy: string
  }
  suites: {
    sortBy: "asc" | "desc"
    filterBy: string
  }
}

export const updateTreeSettingsLS = (settings: TreeSettings) => {
  const prevState = getTreeSettingsLS()
  window.localStorage.setItem("treeSettings", JSON.stringify({ ...prevState, ...settings }))
}

export const getTreeSettingsLS = (): TreeSettings => {
  const settings = window.localStorage.getItem("treeSettings")
  return settings
    ? (JSON.parse(settings) as TreeSettings)
    : {
        collapsed: false,
        show_archived: false,
        plans: { sortBy: "asc", filterBy: "name" },
        suites: { sortBy: "asc", filterBy: "name" },
      }
}

export const refetchNodeAfterCreateOrCopy = async <T extends BaseEntity>(
  treebar: LazyTreeApi<Suite, LazyNodeProps> | LazyTreeApi<TestPlan, LazyNodeProps>,
  updatedEntity: T
) => {
  const id = updatedEntity?.parent?.id ?? null
  if (!id) {
    await treebar.initRoot()
    return
  }

  const findUpdatedNode = treebar.findById(id)
  if (!findUpdatedNode) {
    return
  }

  findUpdatedNode.updateProps({ canOpen: true })
  await treebar.refetchNodeBy((node) => node.id === id)
}

export const refetchNodeAfterArchive = async <T extends BaseEntity>(
  treebar: LazyTreeApi<Suite, LazyNodeProps> | LazyTreeApi<TestPlan, LazyNodeProps>,
  updatedEntity: T
) => {
  const id = updatedEntity?.parent?.id ?? null
  await treebar.refetchNodeBy((node) => node.id === id)
}

export const refetchNodeAfterDelete = async <T extends BaseEntity>(
  treebar: LazyTreeApi<Suite, LazyNodeProps> | LazyTreeApi<TestPlan, LazyNodeProps>,
  updatedEntity: T
) => {
  const id = updatedEntity?.parent?.id ?? null

  if (!id) {
    await treebar.initRoot()
    return
  }

  const findUpdatedNode = treebar.findById(id)
  if (!findUpdatedNode) {
    return
  }

  await treebar.refetchNodeBy((node) => node.id === id)
  findUpdatedNode.updateProps({
    canOpen: !!findUpdatedNode.children.length,
  })
}

export const refetchNodeAfterEdit = async <U extends BaseEntity, O extends BaseEntity>(
  treebar: LazyTreeApi<Suite, LazyNodeProps> | LazyTreeApi<TestPlan, LazyNodeProps>,
  updatedEntity: U,
  oldEntity: O,
  getAncestors: (id: number) => Promise<number[]>
) => {
  if (!updatedEntity.parent?.id || !oldEntity.parent?.id) {
    await treebar.initRoot()
    return
  }

  const findNewParentNode = treebar.findById(updatedEntity.parent.id)
  const findPrevParentNode = treebar.findById(oldEntity.parent.id)

  if (updatedEntity.parent.id === oldEntity.parent.id && findNewParentNode) {
    await treebar.refetchNodeBy((node) => node.id === findNewParentNode.id)
    return
  }

  if (findNewParentNode) {
    await treebar.refetchNodeBy((node) => node.id === findNewParentNode.id)

    if (findNewParentNode.children.length) {
      findNewParentNode.updateProps({ canOpen: true })
    }
  } else {
    // if not found node in tree, need auto open to new path
    const data = await getAncestors(updatedEntity.id)
    for (const openId of data) {
      await treebar.refetchNodeBy((node) => node.id === openId)
    }
  }

  if (findPrevParentNode) {
    await treebar.refetchNodeBy((node) => node.id === findPrevParentNode.id)

    if (!findPrevParentNode.children.length) {
      findPrevParentNode.updateProps({ canOpen: false })
    }
  }
}

export const saveUrlParamByKeys = (
  paramKeys: string[],
  searchParams: URLSearchParams
): URLSearchParams => {
  const params = new URLSearchParams()
  paramKeys.forEach((key) => {
    const value = searchParams.get(key)
    if (value) {
      params.append(key, value)
    }
  })
  return params
}
