export const filterActionFormat = (actions: string[]) => {
  return actions
    .map((action) => {
      switch (action) {
        case "added":
          return "+"
        case "deleted":
          return "-"
        case "updated":
          return "~"

        default:
          return ""
      }
    })
    .join(",")
}
