import { Form } from "antd"
import {
  Control,
  Controller,
  FieldErrors,
  FieldValues,
  Path,
  RegisterOptions,
} from "react-hook-form"

import { LazyGetTriggerType } from "app/export-types"

import { LazyNodeProps, LazyTreeNodeApi } from "shared/libs/tree"

import { BaseSearchEntity, LazyTreeSearch } from "widgets/lazy-tree-search/lazy-tree-search"

interface Props<T extends FieldValues> {
  id: string
  control: Control<T>
  name: Path<T>
  projectId: string
  getData: LazyGetTriggerType<T>
  getAncestors: LazyGetTriggerType<T>
  onSelect: (value: SelectData | null) => void
  label?: string
  placeholder?: string
  formErrors?: FieldErrors<T>
  externalErrors?: FieldValues | null
  required?: boolean
  dataParams?: Record<string, unknown>
  skipInit?: boolean
  selected?: SelectData | null
  rules?: Omit<
    RegisterOptions<T, Path<T>>,
    "valueAsNumber" | "valueAsDate" | "setValueAs" | "disabled"
  >
}

export const LazyTreeSearchFormItem = <T extends FieldValues>({
  id,
  control,
  name,
  label,
  formErrors,
  externalErrors,
  placeholder,
  required = false,
  getData,
  getAncestors,
  onSelect,
  dataParams,
  skipInit = false,
  selected,
  rules = {},
}: Props<T>) => {
  const errors = (formErrors?.[name]?.message ?? externalErrors?.[name]) as string | undefined

  return (
    <Form.Item
      label={label}
      validateStatus={errors ? "error" : ""}
      help={errors}
      required={required}
    >
      <Controller
        // @ts-ignore
        name="parent"
        control={control}
        rules={rules}
        render={() => (
          <LazyTreeSearch
            id={id}
            // @ts-ignore
            getData={getData}
            // @ts-ignore
            getAncestors={getAncestors}
            skipInit={skipInit}
            dataParams={dataParams}
            placeholder={placeholder}
            // @ts-ignore
            onSelect={(node: LazyTreeNodeApi<BaseSearchEntity, LazyNodeProps> | null) =>
              onSelect(node ? { label: node.title, value: node.id as number } : null)
            }
            selectedId={selected?.value}
            searchValue={selected?.label?.toString() ?? ""}
          />
        )}
      />
    </Form.Item>
  )
}
