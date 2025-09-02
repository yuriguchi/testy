export const customAttributesObject: Record<string, CustomAttributeTypes> = {
  0: "Text",
  1: "List",
  2: "JSON",
}

export const customAttributeTypes = Object.entries(customAttributesObject).map(
  ([attributeNum, attributeText]) => ({
    value: Number(attributeNum),
    label: attributeText,
  })
)
