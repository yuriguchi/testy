export const labelsObject: Record<string, LabelTypes> = {
  0: "System",
  1: "Custom",
}

export const labelTypes = Object.entries(labelsObject).map(([labelNum, labelText]) => ({
  value: Number(labelNum),
  label: labelText,
}))
