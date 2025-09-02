interface CustomAttributeState {
  modal: {
    isShow: boolean
    isEditMode: boolean
  }
  attribute?: CustomAttribute
}

interface CustomAttribute {
  id: number
  url: string
  project: number
  type: number
  name: string
  is_deleted: boolean
  applied_to: CustomAttributeAppliedTo
}

interface GetCustomAttributesParams {
  project: string
  test?: number
}

interface CustomAttributeAppliedItemBase {
  is_active: boolean
  is_required: boolean
}

interface CustomAttributeAppliedItemTestCase extends CustomAttributeAppliedItemBase {
  is_active: boolean
  is_required: boolean
  is_suite_specific: boolean
  suite_ids: number[]
}

interface CustomAttributeAppliedItemTestResult extends CustomAttributeAppliedItemBase {
  is_required: boolean
  is_suite_specific: boolean
  suite_ids: number[]
  status_specific: number[]
}

type CustomAttributeModelType = "testresult" | "testcase" | "testplan" | "testsuite"

interface CustomAttributeAppliedToUpdate {
  testresult: CustomAttributeAppliedItemTestResult
  testcase: CustomAttributeAppliedItemTestCase
  testplan: CustomAttributeAppliedItemBase
  testsuite: CustomAttributeAppliedItemBase
}

interface CustomAttributeAppliedTo {
  testresult: Omit<CustomAttributeAppliedItemTestResult, "is_suite_specific">
  testcase: Omit<CustomAttributeAppliedItemTestCase, "is_suite_specific">
  testplan: CustomAttributeAppliedItemBase
  testsuite: CustomAttributeAppliedItemBase
}

interface CustomAttributeUpdate {
  project: number
  name: string
  type: number
  applied_to: CustomAttributeAppliedToUpdate
}

type CustomAttributeTypes = "Text" | "List" | "JSON"

interface CustomAttributeContentTypeItemResponse {
  id: number
  app_label: string
  model: string
  name: string
}

type CustomAttributeContentTypesResponse = CustomAttributeContentTypeItemResponse[]

interface CustomAttributeContentType {
  id: number
  app_label: string
  model: CustomAttributeModelType
  name: string
}
