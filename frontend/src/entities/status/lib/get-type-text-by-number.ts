export const getStatusTypeTextByNumber = (type: number): string => {
  switch (type) {
    case 0:
      return "System"
    case 1:
      return "Custom"

    default:
      return "None"
  }
}
