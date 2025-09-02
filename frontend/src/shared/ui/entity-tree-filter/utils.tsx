import { HighLighterTesty } from "shared/ui"

export interface FilterWithKey extends TestPlanSuite {
  key: string
  value: string
  title: string | React.ReactNode
  titleText: string
  children: FilterWithKey[]
}

export interface FilterFormat<T> {
  data: T[]
  titleKey: "name" | "title"
  searchValue?: string
  newList?: FilterWithKey[]
  allSelectedData?: number[]
}

export interface BaseTreeFilterNode {
  id: Id
  title?: string
  name?: string
  children: BaseTreeFilterNode[]
  parent?: BaseTreeFilterNode
}

export const treeFilterFormat = <T extends BaseTreeFilterNode>({
  data,
  searchValue,
  newList = [],
  allSelectedData = [],
  titleKey,
}: FilterFormat<T>): [FilterWithKey[], number[]] => {
  const genNode = (node: T, children: FilterWithKey[]) => ({
    ...node,
    key: String(node.id),
    value: String(node.id),
    title: (
      <HighLighterTesty searchWords={searchValue ?? ""} textToHighlight={node[titleKey] ?? ""} />
    ),
    titleText: node[titleKey] ?? "",
    name: node[titleKey] ?? "",
    children,
  })

  for (const node of data) {
    allSelectedData.push(Number(node.id))

    if (node.children.length) {
      const [children] = treeFilterFormat({
        data: node.children,
        searchValue,
        newList: [],
        allSelectedData,
        titleKey,
      })
      newList.push(genNode(node, children))
    } else {
      newList.push(genNode(node, []))
    }
  }

  return [newList, allSelectedData]
}
