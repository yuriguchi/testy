import { Col, Form, Input, Row, Tabs } from "antd"
import { CustomAttributeAdd, CustomAttributeForm } from "entities/custom-attribute/ui"
import { Controller } from "react-hook-form"
import { useTranslation } from "react-i18next"

import { LabelWrapper } from "entities/label/ui"

import { TestCaseStepsBlock } from "entities/test-case/ui/steps/block"

import { config } from "shared/config"
import { ErrorObj } from "shared/hooks"
import {
  AlertError,
  Attachment,
  FormViewHeader,
  InfoTooltipBtn,
  TextAreaWithAttach,
} from "shared/ui"

import { ScenarioLabelFormTestCase } from "./scenario-label-form-test-case"
import styles from "./styles.module.css"
import { useTestCaseCreateView } from "./use-test-case-create-view"

export const CreateTestCaseView = () => {
  const { t } = useTranslation()
  const {
    isLoading,
    errors,
    formErrors,
    control,
    attachments,
    attachmentsIds,
    steps,
    isSteps,
    isDirty,
    tab,
    attributes,
    labelProps,
    onLoad,
    onRemove,
    onChange,
    setValue,
    setAttachments,
    handleCancel,
    handleSubmitForm,
    register,
    handleTabChange,
    addAttribute,
    onAttributeChangeName,
    onAttributeChangeType,
    onAttributeChangeValue,
    onAttributeRemove,
  } = useTestCaseCreateView()

  const scenarioFormErrors = !isSteps
    ? (formErrors.scenario?.message ?? errors?.scenario ?? "")
    : !steps.length
      ? t("Required field")
      : ""

  return (
    <>
      <FormViewHeader
        model="test-case"
        type="create"
        isDisabledSubmit={!isDirty}
        isLoadingSubmit={isLoading}
        onSubmit={handleSubmitForm}
        onClose={handleCancel}
        title={
          <>
            {t("Create")} {t("Test")} {t("Case")}
          </>
        }
      />

      {errors ? (
        <AlertError
          error={errors as ErrorObj}
          skipFields={["name", "setup", "scenario", "teardown", "estimate", "attributes"]}
        />
      ) : null}

      <Form id="create-test-case-form" layout="vertical" onFinish={handleSubmitForm}>
        <Tabs defaultActiveKey="general" onChange={handleTabChange} activeKey={tab}>
          <Tabs.TabPane tab={t("General")} key="general">
            <Row gutter={[32, 32]} style={{ marginTop: 14 }}>
              <Col span={12}>
                <Form.Item
                  label={t("Name")}
                  validateStatus={(formErrors.name?.message ?? errors?.name) ? "error" : ""}
                  help={formErrors.name?.message ?? errors?.name ?? ""}
                  required
                >
                  <Controller
                    name="name"
                    control={control}
                    rules={{ required: t("Required field") }}
                    render={({ field }) => <Input {...field} id="create-name-input" />}
                  />
                </Form.Item>
                <Form.Item
                  label={t("Description")}
                  validateStatus={errors?.description ? "error" : ""}
                  help={errors?.description ? errors.description : ""}
                >
                  <Controller
                    name="description"
                    control={control}
                    render={({ field }) => (
                      <TextAreaWithAttach
                        uploadId="create-description"
                        textAreaId="create-description-textarea"
                        fieldProps={field}
                        stateAttachments={{ attachments, setAttachments }}
                        customRequest={onLoad}
                        setValue={setValue}
                      />
                    )}
                  />
                </Form.Item>
                <Form.Item
                  label={t("Setup")}
                  validateStatus={errors?.setup ? "error" : ""}
                  help={errors?.setup ? errors.setup : ""}
                >
                  <Controller
                    name="setup"
                    control={control}
                    render={({ field }) => (
                      <TextAreaWithAttach
                        uploadId="create-setup"
                        textAreaId="create-setup-textarea"
                        fieldProps={field}
                        stateAttachments={{ attachments, setAttachments }}
                        customRequest={onLoad}
                        setValue={setValue}
                      />
                    )}
                  />
                </Form.Item>
                {!isSteps && (
                  <Form.Item
                    label={<ScenarioLabelFormTestCase control={control} />}
                    validateStatus={scenarioFormErrors ? "error" : ""}
                    help={scenarioFormErrors}
                    required
                    className={styles.formItem}
                  >
                    <Controller
                      name="scenario"
                      control={control}
                      render={({ field }) => (
                        <TextAreaWithAttach
                          uploadId="create-scenario"
                          textAreaId="create-scenario-textarea"
                          customRequest={onLoad}
                          fieldProps={field}
                          stateAttachments={{ attachments, setAttachments }}
                          setValue={setValue}
                        />
                      )}
                    />
                  </Form.Item>
                )}
                {isSteps && (
                  <Form.Item
                    label={<ScenarioLabelFormTestCase control={control} />}
                    validateStatus={scenarioFormErrors ? "error" : ""}
                    help={scenarioFormErrors}
                    required
                    className={styles.formItem}
                  >
                    <Controller
                      name="steps"
                      control={control}
                      render={({ field }) => (
                        <TestCaseStepsBlock steps={field.value ?? []} setSteps={field.onChange} />
                      )}
                    />
                  </Form.Item>
                )}
                {!isSteps && (
                  <Form.Item
                    label={t("Expected")}
                    validateStatus={errors?.expected ? "error" : ""}
                    help={errors?.expected ? errors.expected : ""}
                  >
                    <Controller
                      name="expected"
                      control={control}
                      render={({ field }) => (
                        <TextAreaWithAttach
                          uploadId="create-expected"
                          textAreaId="create-expected-textarea"
                          fieldProps={field}
                          stateAttachments={{ attachments, setAttachments }}
                          customRequest={onLoad}
                          setValue={setValue}
                        />
                      )}
                    />
                  </Form.Item>
                )}
                <Form.Item
                  label={t("Teardown")}
                  validateStatus={errors?.teardown ? "error" : ""}
                  help={errors?.teardown ? errors.teardown : ""}
                >
                  <Controller
                    name="teardown"
                    control={control}
                    render={({ field }) => (
                      <TextAreaWithAttach
                        uploadId="create-teardown"
                        textAreaId="create-teardown-textarea"
                        fieldProps={field}
                        stateAttachments={{ attachments, setAttachments }}
                        customRequest={onLoad}
                        setValue={setValue}
                      />
                    )}
                  />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  label={t("Estimate")}
                  validateStatus={errors?.estimate ? "error" : ""}
                  help={errors?.estimate ? errors.estimate : ""}
                >
                  <Controller
                    name="estimate"
                    control={control}
                    render={({ field }) => (
                      <Input
                        {...field}
                        id="create-estimate-input"
                        data-testid="create-estimate-input"
                        value={field.value ?? ""}
                        suffix={<InfoTooltipBtn title={config.estimateTooltip} />}
                      />
                    )}
                  />
                </Form.Item>
                <Form.Item
                  label={t("Labels")}
                  validateStatus={errors?.labels ? "error" : ""}
                  help={errors?.labels ? errors.labels : ""}
                >
                  <Controller
                    name="labels"
                    control={control}
                    render={({ field }) => (
                      <LabelWrapper labelProps={labelProps} fieldProps={field} />
                    )}
                  />
                </Form.Item>
                <Controller
                  name="attributes"
                  control={control}
                  render={({ field }) => (
                    <Row style={{ flexDirection: "column", marginTop: steps.length ? 24 : 0 }}>
                      <CustomAttributeForm
                        attributes={attributes}
                        onChangeName={onAttributeChangeName}
                        onChangeType={onAttributeChangeType}
                        onChangeValue={onAttributeChangeValue}
                        onRemove={onAttributeRemove}
                        onBlur={field.onBlur}
                        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
                        errors={errors?.attributes ? JSON.parse(errors?.attributes) : undefined}
                      />
                      <CustomAttributeAdd onClick={addAttribute} />
                    </Row>
                  )}
                />
              </Col>
            </Row>
          </Tabs.TabPane>
          <Tabs.TabPane tab={t("Attachments")} key="attachments">
            <Attachment.DropFiles
              attachments={attachments}
              attachmentsIds={attachmentsIds}
              onChange={onChange}
              onLoad={onLoad}
              onRemove={onRemove}
              register={register}
              idInput="create-test-case-attachments-input"
            />
          </Tabs.TabPane>
        </Tabs>
      </Form>
    </>
  )
}
