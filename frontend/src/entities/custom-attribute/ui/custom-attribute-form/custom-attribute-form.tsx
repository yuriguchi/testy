import { Noop } from "react-hook-form"

import { CustomAttributeFormItem } from "../custom-attribute-form-item/custom-attribute-form-item"
import styles from "./styles.module.css"

interface Props {
  attributes: Attribute[]
  onChangeName: (id: string, name: string) => void
  onChangeType: (id: string, type: AttributeType) => void
  onChangeValue: (id: string, value: string) => void
  onRemove: (id: string) => void
  onBlur?: Noop
  errors?: Record<string, Record<string, string>>
}

export const CustomAttributeForm = ({
  attributes,
  onChangeName,
  onChangeType,
  onChangeValue,
  onRemove,
  onBlur,
  errors,
}: Props) => {
  if (attributes.length === 0) return null
  return (
    <div className={styles.list}>
      {attributes.map((attribute, index) => {
        return (
          <CustomAttributeFormItem
            key={attribute.id}
            index={index}
            attribute={attribute}
            onChangeName={onChangeName}
            onChangeType={onChangeType}
            onChangeValue={onChangeValue}
            onRemove={onRemove}
            errorName={errors?.[attribute.id]?.name}
            errorValue={errors?.[attribute.id]?.value}
            onBlur={onBlur}
          />
        )
      })}
    </div>
  )
}
