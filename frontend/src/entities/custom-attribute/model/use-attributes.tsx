import { useEffect, useState } from "react"

import { makeRandomId } from "shared/libs"

interface UseAttributesProps {
  mode: "create" | "edit"
  setValue: (attributes: Attribute[]) => void
  initAttributes: Attribute[]
  addAttributeAdditionalParams?: Record<string, unknown>
  getJsonAdditionalParams?: Record<string, unknown>
}

export const useAttributes = ({
  mode,
  initAttributes,
  addAttributeAdditionalParams,
  getJsonAdditionalParams,
  setValue,
}: UseAttributesProps) => {
  const [attributes, setAttributes] = useState<Attribute[]>([])

  useEffect(() => {
    if (mode === "create" && initAttributes.length) {
      setAttributes(initAttributes)
    }
  }, [mode, initAttributes])

  const addAttribute = () => {
    const newAttributes = [
      ...attributes,
      {
        id: makeRandomId(),
        name: "",
        value: "",
        type: "Text",
        is_init: false,
        ...addAttributeAdditionalParams,
      },
    ] as Attribute[]
    setAttributes(newAttributes)
    setValue(newAttributes)
  }

  const onAttributeRemove = (attributeId: string) => {
    const newAttributes = attributes.filter(({ id }: Attribute) => id !== attributeId)
    setAttributes(newAttributes)
    setValue(newAttributes)
  }

  const onAttributeChangeName = (attributeId: string, name: string) => {
    const newAttributes = attributes.map((attribute) => {
      if (attribute.id !== attributeId) return attribute
      return {
        ...attribute,
        name,
      }
    })
    setAttributes(newAttributes)
    setValue(newAttributes)
  }

  const onAttributeChangeValue = (attributeId: string, value: string) => {
    const newAttributes = attributes.map((attribute) => {
      if (attribute.id !== attributeId) return attribute
      return {
        ...attribute,
        value,
      }
    })
    setAttributes(newAttributes)
    setValue(newAttributes)
  }

  const onAttributeChangeType = (attributeId: string, type: AttributeType) => {
    const newAttributes = attributes.map((attribute) => {
      if (attribute.id !== attributeId) return attribute
      return {
        ...attribute,
        type,
      }
    })
    setAttributes(newAttributes)
    setValue(newAttributes)
  }

  const resetAttributes = () => {
    setAttributes(mode === "create" ? initAttributes : [])
  }

  const getAttributeJson = (attributesJson: AttributesObject) => {
    const newAttributes: Attribute[] = []

    Object.keys(attributesJson).map((key: string) => {
      if (typeof attributesJson[key] === "string") {
        newAttributes.push({
          id: makeRandomId(),
          name: key,
          type: "Text",
          value: attributesJson[key],
          is_init: false,
          ...getJsonAdditionalParams,
        })
      } else if (Array.isArray(attributesJson[key])) {
        const array: string[] = attributesJson[key] as string[]
        newAttributes.push({
          id: makeRandomId(),
          name: key,
          type: "List",
          value: array.join("\r\n"),
          is_init: false,
          ...getJsonAdditionalParams,
        })
      } else if (typeof attributesJson[key] === "object") {
        newAttributes.push({
          id: makeRandomId(),
          name: key,
          type: "JSON",
          value: JSON.stringify(attributesJson[key], null, 2),
          is_init: false,
          ...getJsonAdditionalParams,
        })
      }
    })

    // add missing custom attributes
    initAttributes.forEach((attr) => {
      const existingAttribute = newAttributes.find((lookupAttr) => lookupAttr.name === attr.name)
      if (!existingAttribute) {
        newAttributes.push(attr)
      } else if (attr.type !== existingAttribute.type) {
        existingAttribute.type = attr.type
      } else if (attr.required && !existingAttribute.required) {
        existingAttribute.required = attr.required as boolean
      } else {
        existingAttribute.is_init = true
      }
    })

    return newAttributes
  }

  return {
    attributes,
    setAttributes,
    resetAttributes,
    addAttribute,
    onAttributeChangeType,
    onAttributeChangeValue,
    onAttributeChangeName,
    onAttributeRemove,
    getAttributeJson,
  }
}
