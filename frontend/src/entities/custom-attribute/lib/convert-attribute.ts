import { customAttributesObject } from "shared/config/custom-attribute-types"

interface Props {
  model: CustomAttributeModelType
  attribute: CustomAttribute
  is_init?: boolean
}

export const convertAttribute = ({ model, attribute, is_init = true }: Props): Attribute => {
  const hasStatusSpecific = model === "testresult"
  const appliedTo = attribute.applied_to[model] as CustomAttributeAppliedItemTestResult

  return {
    id: String(attribute.id),
    name: attribute.name,
    type: customAttributesObject[attribute.type],
    value: "",
    required: appliedTo?.is_required ?? false,
    status_specific: hasStatusSpecific ? appliedTo.status_specific : [],
    is_init,
  }
}
