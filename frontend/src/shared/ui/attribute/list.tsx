import { ControllerRenderProps } from "react-hook-form"

import { AttributForm } from "./form"
import styles from "./styles.module.css"

interface AttributeListProps {
  errors?: Record<string, Record<string, string>>
  fieldProps:
    | ControllerRenderProps<ResultFormData, "attributes">
    | ControllerRenderProps<TestCaseFormData, "attributes">
  attributes: Attribute[]
  handleAttributeRemove: (attributeId: string) => void
  handleAttributeChangeName: (attributeId: string, name: string) => void
  handleAttributeChangeValue: (attributeId: string, value: string) => void
  handleAttributeChangeType: (attributeId: string, type: AttributeType) => void
}

export const AttributeList = ({
  errors,
  fieldProps,
  attributes,
  handleAttributeRemove,
  handleAttributeChangeName,
  handleAttributeChangeValue,
  handleAttributeChangeType,
}: AttributeListProps) => {
  if (attributes.length === 0) return null
  return (
    <div className={styles.list}>
      {attributes.map((attribut, index) => {
        return (
          <AttributForm
            index={index}
            key={attribut.id}
            errors={errors ? errors[attribut.id] : undefined}
            fieldProps={fieldProps}
            attribut={attribut}
            handleAttributeRemove={handleAttributeRemove}
            handleAttributeChangeName={handleAttributeChangeName}
            handleAttributeChangeValue={handleAttributeChangeValue}
            handleAttributeChangeType={handleAttributeChangeType}
          />
        )
      })}
    </div>
  )
}
