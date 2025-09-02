export const SYSTEM_TYPE = 0
export const CUSTOM_TYPE = 1

export const statusesObject: Record<string, StatusTypes> = {
  [SYSTEM_TYPE]: "System",
  [CUSTOM_TYPE]: "Custom",
}

export const statusTypes = Object.entries(statusesObject).map(([statusNum, statusText]) => ({
  value: Number(statusNum),
  label: statusText,
}))
