export const generateProjectIconTitle = (fullName: string) => {
  const splitName = fullName.split(" ")
  const clearName = splitName.filter(Boolean)
  if (clearName.length < 2) return fullName.charAt(0).toUpperCase()

  return clearName
    .map((el) => Array.from(el)[0].toUpperCase())
    .slice(0, 3)
    .join("")
}
