interface ParameterState {
  parameter: IParameter | null
  modal: {
    isShow: boolean
    isEditMode: boolean
  }
}

interface IParameter {
  id: Id
  project: number
  data: string
  group_name: string
  url: string
}

interface IParameterTreeView {
  key: string | number
  title: string
  value: string | number
  children?: IParameterTreeView[]
}

interface IParameterUpdate {
  project: number
  data: string
  group_name: string
}
