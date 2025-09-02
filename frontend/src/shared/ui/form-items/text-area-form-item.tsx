import { Form, Input } from "antd"
import {
  Control,
  Controller,
  FieldErrors,
  FieldValues,
  Path,
  RegisterOptions,
} from "react-hook-form"
import { useTranslation } from "react-i18next"

import { capitalizeFirstLetter } from "shared/libs"

interface Props<T extends FieldValues> {
  id: string
  control: Control<T>
  name: Path<T>
  formErrors?: FieldErrors<T>
  externalErrors?: FieldValues | null
  label?: string
  required?: boolean
  rules?: Omit<
    RegisterOptions<T, Path<T>>,
    "valueAsNumber" | "valueAsDate" | "setValueAs" | "disabled"
  >
  maxLength?: number
}

export const TextAreaFormItem = <T extends FieldValues>({
  id,
  control,
  name,
  label = capitalizeFirstLetter(name),
  formErrors,
  externalErrors,
  rules,
  required = false,
  maxLength,
}: Props<T>) => {
  const { t } = useTranslation()
  const errors = (
    formErrors ? formErrors[name]?.message : externalErrors ? externalErrors[name] : undefined
  ) as string | undefined

  return (
    <Form.Item
      label={label}
      validateStatus={errors ? "error" : ""}
      help={errors}
      required={required}
    >
      <Controller
        name={name}
        control={control}
        rules={{
          required: required ? { value: true, message: t("Required field") } : undefined,
          maxLength: maxLength
            ? { value: maxLength, message: "Максимальная длина " + maxLength }
            : undefined,
          ...rules,
        }}
        render={({ field }) => <Input.TextArea id={id} rows={4} {...field} />}
      />
    </Form.Item>
  )
}
