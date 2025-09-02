interface Label {
  id?: string | number
  name: string
  project: number
  type: number
  url: string
  user: null
}

interface LabelInForm {
  id?: string | number
  name: string
}

interface GetLabelsParams {
  project: string
}

interface LabelUpdate {
  project: number
  name: string
  type: number
}

type LabelTypes = "System" | "Custom"
type LabelCondition = "and" | "or"
