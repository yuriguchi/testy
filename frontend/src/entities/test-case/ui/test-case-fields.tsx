import { useTranslation } from "react-i18next"

import { LabelField } from "entities/label/ui"

import { Attachment, AttributesObjectView, Field, FieldWithHide, Steps } from "shared/ui"

interface TestCaseFieldsProps {
  testCase: TestCase
}

export const TestCaseFields = ({ testCase }: TestCaseFieldsProps) => {
  const { t } = useTranslation()
  return (
    <>
      {!!testCase.labels.length && <LabelField title={t("Labels")} labels={testCase.labels} />}
      {testCase.test_suite_description && (
        <FieldWithHide
          id="test-suite-description"
          title="Test Suite description"
          value={testCase.test_suite_description}
        />
      )}
      <Field id="test-case-desc" markdown title={t("Description")} value={testCase.description} />
      <Field id="test-case-setup" markdown title={t("Setup")} value={testCase.setup} />
      {testCase.steps.length ? (
        <Steps.Field steps={[...testCase.steps].sort((a, b) => a.sort_order - b.sort_order)} />
      ) : (
        <Field
          id="test-case-scenario"
          markdown
          title={t("Scenario")}
          value={testCase.scenario ?? ""}
        />
      )}
      {!testCase.steps.length && (
        <Field
          id="test-case-expected"
          markdown
          title={t("Expected")}
          value={testCase.expected ?? ""}
        />
      )}
      <Field id="test-case-teardown" markdown title="Teardown" value={testCase.teardown} />
      <Field id="test-case-estimate" title={t("Estimate")} value={testCase.estimate ?? ""} />
      {!!testCase.attributes && !!Object.keys(testCase.attributes).length && (
        <Field
          id="test-case-attributes"
          title={t("Attributes")}
          value={<AttributesObjectView attributes={testCase.attributes} />}
        />
      )}

      {!!testCase.attachments.length && <Attachment.Field attachments={testCase.attachments} />}
    </>
  )
}
