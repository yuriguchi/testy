import { Form, TreeSelect } from "antd"
import { DataNode } from "antd/es/tree"
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
  treeData: DataNode[]
  label?: string
  formErrors?: FieldErrors<T>
  externalErrors?: FieldValues | null
  required?: boolean
  rules?: Omit<
    RegisterOptions<T, Path<T>>,
    "valueAsNumber" | "valueAsDate" | "setValueAs" | "disabled"
  >
  treeProps?: React.ComponentProps<typeof TreeSelect>
}

export const TreeSelectFormItem = <T extends FieldValues>({
  id,
  control,
  name,
  formErrors,
  externalErrors,
  rules,
  label = capitalizeFirstLetter(name),
  required = false,
  treeData,
  treeProps,
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
          ...rules,
        }}
        render={({ field }) => (
          <div data-testid={`${id}-select`}>
            <TreeSelect
              id={id}
              {...field}
              showSearch
              treeCheckable
              treeNodeFilterProp="title"
              style={{ width: "100%" }}
              dropdownStyle={{ maxHeight: 400, overflow: "auto" }}
              treeData={treeData}
              placeholder={t("Please select")}
              allowClear
              showCheckedStrategy="SHOW_CHILD"
              {...treeProps}
            />
          </div>
        )}
      />
    </Form.Item>
  )
}
