import { DatePicker, Form } from "antd"
import { Dayjs } from "dayjs"
import {
  Control,
  Controller,
  FieldErrors,
  FieldValues,
  Path,
  PathValue,
  RegisterOptions,
} from "react-hook-form"
import { useTranslation } from "react-i18next"

import { capitalizeFirstLetter } from "shared/libs"

interface Props<T extends FieldValues> {
  id: string
  control: Control<T>
  name: Path<T>
  setDate: (value: React.SetStateAction<Dayjs | null>) => void
  disabledDate: (current: Dayjs) => boolean
  defaultDate?: PathValue<T, Path<T>>
  label?: string
  formErrors?: FieldErrors<T>
  externalErrors?: FieldValues | null
  required?: boolean
  rules?: Omit<
    RegisterOptions<T, Path<T>>,
    "valueAsNumber" | "valueAsDate" | "setValueAs" | "disabled"
  >
  maxLength?: number
  formStyles?: React.CSSProperties
}

export const DateFormItem = <T extends FieldValues>({
  id,
  control,
  name,
  setDate,
  disabledDate,
  defaultDate,
  formErrors,
  externalErrors,
  rules,
  maxLength,
  label = capitalizeFirstLetter(name),
  required = false,
  formStyles,
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
      style={formStyles}
    >
      <Controller
        name={name}
        control={control}
        defaultValue={defaultDate}
        rules={{
          required: required ? { value: true, message: t("Required field") } : undefined,
          maxLength: maxLength
            ? { value: maxLength, message: `${t("Maximum length")} ` + maxLength }
            : undefined,
          ...rules,
        }}
        render={(propsController) => (
          <DatePicker
            id={id}
            {...propsController}
            style={{ width: "100%" }}
            value={propsController.field.value}
            onChange={(e) => {
              // @ts-ignore
              propsController.field.onChange(e)
              setDate(e)
            }}
            disabledDate={disabledDate}
          />
        )}
      />
    </Form.Item>
  )
}
