interface Role {
  id: number
  name: string
  permissions: number[]
  type: number
  url: string
}

interface RoleUpdate {
  name: string
  permissions: number[]
  type: 0 | 1
}

interface AssignRole {
  roles: number[]
  user: number
  project: number
}

interface UnassignRole {
  user: number
  project: number
}

interface Permission {
  id: number
  name: string
  codename: string
}

interface RoleState {
  isModalOpen: boolean
  mode: "create" | "edit"
  user: UserWithRoles | null
  onSuccess: (() => Promise<void>) | null
}
