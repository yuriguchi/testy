/* eslint-disable @typescript-eslint/prefer-for-of */

export const makeAttributesJson = (attributes: Attribute[]) => {
  const attributesJson: AttributesObject = {}
  let isSuccess = true
  const errors: Record<string, Record<string, string>> = {}

  for (let i = 0; i < attributes.length; i++) {
    const name = attributes[i].name.trimStart().trimEnd()
    // eslint-disable-next-line @typescript-eslint/no-base-to-string
    const value = attributes[i].value.toString()
    const type = attributes[i].type
    const isRequired = !!attributes[i].required

    if (name === "" || (value === "" && isRequired)) {
      errors[attributes[i].id] = {
        name: name === "" ? "Required" : "",
        value: value === "" && isRequired ? "Required" : "",
      }
      isSuccess = false
      continue
    }

    if (value === "" && isRequired) {
      errors[attributes[i].id] = { ...errors[attributes[i].id], value: "Required" }
      isSuccess = false
      continue
    }

    if (value === "") {
      continue
    }

    if (type === "JSON") {
      try {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        attributesJson[name] = JSON.parse(value)
      } catch (err: unknown) {
        errors[attributes[i].id] = { ...errors[attributes[i].id], value: "JSON parse error" }
        isSuccess = false
        continue
      }
    } else if (type === "List") {
      attributesJson[name] = value.split(/\r?\n/)
    } else if (type === "Text") {
      attributesJson[name] = attributes[i].value
    }
  }

  return { attributesJson, isSuccess, errors }
}
