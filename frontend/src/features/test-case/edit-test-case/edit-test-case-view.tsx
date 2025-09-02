import { Button, Col, Dropdown, Form, Input, MenuProps, Row, Tabs } from "antd"
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
  ContainerLoader,
  FormViewHeader,
  InfoTooltipBtn,
  TextAreaWithAttach,
} from "shared/ui"

import { ScenarioLabelFormTestCase } from "../create-test-case/scenario-label-form-test-case"
import { SelectSuiteTestCase } from "../select-suite-test-case/select-suite-test-case"
import styles from "./styles.module.css"
import { useTestCaseEditView } from "./use-test-case-edit-view"

export const EditTestCaseView = () => {
  const { t } = useTranslation()
  const {
    title,
    isLoading,
    errors,
    formErrors,
    control,
    attachments,
    attachmentsIds,
    isSteps,
    steps,
    isDirty,
    labelProps,
    tab,
    shouldShowSuiteSelect,
    attributes,
    selectedSuite,
    onLoad,
    onRemove,
    onChange,
    setValue,
    setAttachments,
    handleCancel,
    handleSubmitFormAsCurrent,
    handleSubmitFormAsNew,
    register,
    handleTabChange,
    addAttribute,
    onAttributeChangeType,
    onAttributeChangeValue,
    onAttributeChangeName,
    onAttributeRemove,
    handleSelectSuite,
  } = useTestCaseEditView()

  const scenarioFormErrors = !isSteps
    ? (formErrors.scenario?.message ?? errors?.scenario ?? "")
    : !steps.length
      ? t("Required field")
      : ""

  const items: MenuProps["items"] = [
    {
      key: "1",
      label: (
        <Button
          id="modal-update-test-case-btn"
          key="submit"
          loading={isLoading}
          onClick={handleSubmitFormAsCurrent}
          type="primary"
          disabled={!isDirty}
        >
          {t("Update current version")}
        </Button>
      ),
    },
  ]

  if (isLoading) {
    return <ContainerLoader />
  }

  return (
    <>
      <FormViewHeader
        model="test-case"
        type="edit"
        title={title}
        onClose={handleCancel}
        submitNode={
          <Dropdown.Button
            key="update"
            className="edit-test-case"
            menu={{ items }}
            type={isDirty ? "primary" : undefined}
            loading={isLoading}
            disabled={!isDirty}
            style={{ width: "fit-content", display: "inline-flex" }}
            onClick={handleSubmitFormAsNew}
            size="large"
            data-testid="dropdown-update-button"
          >
            {t("Update")}
          </Dropdown.Button>
        }
      />

      {errors ? (
        <AlertError
          error={errors as ErrorObj}
          skipFields={["name", "setup", "scenario", "teardown", "estimate", "steps", "attributes"]}
        />
      ) : null}

      <Form id="edit-test-case-form" layout="vertical" onFinish={handleSubmitFormAsNew}>
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
                    render={({ field }) => <Input {...field} id="edit-name-input" />}
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
                        uploadId="edit-description"
                        textAreaId="edit-description-textarea"
                        fieldProps={field}
                        stateAttachments={{ attachments, setAttachments }}
                        customRequest={onLoad}
                        setValue={setValue}
                      />
                    )}
                  />
                </Form.Item>
                {shouldShowSuiteSelect && (
                  <Form.Item
                    label={t("Suite")}
                    validateStatus={errors?.suite ? "error" : ""}
                    help={errors?.suite ? errors.suite : ""}
                  >
                    <Controller
                      name="suite"
                      control={control}
                      render={() => (
                        <SelectSuiteTestCase suite={selectedSuite} onChange={handleSelectSuite} />
                      )}
                    />
                  </Form.Item>
                )}
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
                        uploadId="edit-setup"
                        textAreaId="edit-setup-textarea"
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
                          uploadId="edit-scenario"
                          textAreaId="edit-scenario-textarea"
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
                          uploadId="edit-expected"
                          textAreaId="edit-expected-textarea"
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
                        uploadId="edit-teardown"
                        textAreaId="edit-teardown-textarea"
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
                        id="edit-estimate-input"
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
                    <Row style={{ flexDirection: "column", marginTop: 0 }}>
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
              idInput="edit-test-case-attachments-input"
            />
          </Tabs.TabPane>
        </Tabs>
      </Form>
    </>
  )
}
