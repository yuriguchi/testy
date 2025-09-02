import { Button, Col, Divider, Form, Modal, Row, Select } from "antd"
import { CustomAttributeAdd, CustomAttributeForm } from "entities/custom-attribute/ui"
import { Controller } from "react-hook-form"
import { useTranslation } from "react-i18next"

import { ErrorObj } from "shared/hooks/use-alert-error"
import { AlertError, Attachment, Status, Steps, TextAreaWithAttach } from "shared/ui"

import { ApplyToStepsButton } from "../apply-to-steps-button/apply-to-steps-button"
import { CreateResultModalProps, useCreateResultModal } from "./use-create-result-modal"

export const CreateResultModal = (props: CreateResultModalProps) => {
  const { t } = useTranslation()
  const {
    isLoading,
    isLoadingCreateAttachment,
    attachments,
    attachmentsIds,
    control,
    attributes,
    steps,
    errors,
    onLoad,
    onChange,
    onRemove,
    handleSubmitForm,
    handleCancel,
    setValue,
    register,
    addAttribute,
    onAttributeChangeName,
    onAttributeChangeType,
    onAttributeChangeValue,
    onAttributeRemove,
    setSteps,
    setAttachments,
    statuses,
    disabled,
  } = useCreateResultModal(props)

  const { isShow, testCase } = props

  return (
    <Modal
      className="create-result-modal"
      width={1200}
      centered
      title={`${t("Create")} ${t("Result")}`}
      open={isShow}
      onCancel={handleCancel}
      footer={[
        <Button id="cancel-create-result-modal" key="back" onClick={handleCancel}>
          {t("Cancel")}
        </Button>,
        <Button
          id="create-result-modal"
          key="submit"
          type="primary"
          loading={isLoading || isLoadingCreateAttachment}
          onClick={handleSubmitForm}
          disabled={disabled}
        >
          {t("Create")}
        </Button>,
      ]}
    >
      {errors ? (
        <AlertError error={errors as ErrorObj} skipFields={["status", "comment", "attributes"]} />
      ) : null}

      <Form id="create-result-form" layout="vertical" onFinish={handleSubmitForm}>
        <Row>
          <Col flex="1 0">
            <Form.Item
              label={t("Status")}
              validateStatus={errors?.status ? "error" : ""}
              help={
                errors?.status ? errors.status : t("Set the test status (passed, failed etc.).")
              }
            >
              <Controller
                name="status"
                control={control}
                render={({ field }) => (
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <Select
                      {...field}
                      placeholder={t("Please select")}
                      style={{ width: "100%" }}
                      id="create-result-status"
                    >
                      {statuses.map((status) => (
                        <Select.Option key={status.id} value={status.id}>
                          <Status
                            id={status.id}
                            name={status.name}
                            color={status.color}
                            extraId="create-result"
                          />
                        </Select.Option>
                      ))}
                    </Select>
                    <ApplyToStepsButton
                      steps={testCase.steps}
                      status={field.value}
                      onApply={setSteps}
                    />
                  </div>
                )}
              />
            </Form.Item>
            <Form.Item
              label={t("Comment")}
              validateStatus={errors?.comment ? "error" : ""}
              help={errors?.comment ? errors.comment : t("Describe your test result.")}
            >
              <Controller
                name="comment"
                control={control}
                render={({ field }) => (
                  <TextAreaWithAttach
                    uploadId="create-result-comment"
                    textAreaId="create-result-comment-textarea"
                    fieldProps={field}
                    stateAttachments={{ attachments, setAttachments }}
                    customRequest={onLoad}
                    setValue={setValue}
                  />
                )}
              />
            </Form.Item>
            <Attachment.DropFiles
              attachments={attachments}
              attachmentsIds={attachmentsIds}
              onChange={onChange}
              onLoad={onLoad}
              onRemove={onRemove}
              register={register}
              idInput="create-result-attachments-input"
            />
          </Col>
          <Col>
            <Divider type="vertical" style={{ height: "100%" }} />
          </Col>
          <Col flex="1 0">
            {!!testCase.steps.length && (
              <Row style={{ flexDirection: "column" }}>
                <div className="ant-col ant-form-item-label">
                  <label title="Steps">{t("Steps")}</label>
                </div>
                <Steps.ResultInCreateModal testCase={testCase} steps={steps} setSteps={setSteps} />
              </Row>
            )}
            <Form.Item>
              <Controller
                name="attributes"
                control={control}
                render={({ field }) => (
                  <Row
                    style={{ flexDirection: "column", marginTop: testCase.steps.length ? 24 : 0 }}
                  >
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
            </Form.Item>
          </Col>
        </Row>
      </Form>
    </Modal>
  )
}
