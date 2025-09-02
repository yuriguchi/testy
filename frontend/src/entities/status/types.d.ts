interface StatusState {
  modal: {
    isShow: boolean
    mode: ModalMode
    status?: Status
  }
}

interface Status {
  id: number
  url: string
  name: string
  project: number
  type: number
  color: string
}

interface StatusInForm {
  id?: string | number
  name: string
}

interface GetStatusesParams {
  project: string | number
}

interface StatusUpdate {
  project: number
  name: string
  type: number
  color: string
}

type StatusTypes = "System" | "Custom"
