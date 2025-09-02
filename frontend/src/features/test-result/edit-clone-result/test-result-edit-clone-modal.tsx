import { Button, Col, Divider, Form, Modal, Row, Select } from "antd"
import { CustomAttributeAdd, CustomAttributeForm } from "entities/custom-attribute/ui"
import { Controller } from "react-hook-form"
import { useTranslation } from "react-i18next"

import { ErrorObj } from "shared/hooks/use-alert-error"
import { AlertError, Attachment, Status, Steps, TextAreaWithAttach } from "shared/ui"

import { ApplyToStepsButton } from "../apply-to-steps-button/apply-to-steps-button"
import { useEditCloneResultModal } from "./use-edit-clone-result-modal"

interface TestResultEditCopyModalProps {
  isShow: boolean
  setIsShow: React.Dispatch<React.SetStateAction<boolean>>
  testResult: Result
  testCase: TestCase
  isClone: boolean
  onSubmit?: (newResult: Result, oldResult: Result) => void
}

export const TestResultEditCloneModal = ({
  isShow,
  setIsShow,
  testResult,
  testCase,
  isClone,
  onSubmit,
}: TestResultEditCopyModalProps) => {
  const { t } = useTranslation()
  const {
    isLoading,
    errors,
    attachments,
    attachmentsIds,
    control,
    attributes,
    watchSteps,
    setAttachments,
    handleStepsChange,
    handleAttachmentsLoad,
    setValue,
    handleCancel,
    handleSubmitForm,
    addAttribute,
    onAttributeChangeType,
    onAttributeChangeValue,
    onAttributeChangeName,
    onAttributeRemove,
    handleAttachmentsChange,
    handleAttachmentsRemove,
    register,
    statuses,
    isDisabledSubmit,
  } = useEditCloneResultModal({
    isShow,
    setIsShow,
    testResult,
    isClone,
    onSubmit,
  })

  return (
    <Modal
      className={`test-result-edit${isClone ? "-clone" : ""}-modal`}
      width={1200}
      centered
      open={isShow}
      onCancel={handleCancel}
      title={
        !isClone
          ? `${t("Edit Test Result")} '${testResult.id}'`
          : `${t("Clone Test Result")} '${testResult.id}'`
      }
      destroyOnClose
      footer={[
        <Button key="back" onClick={handleCancel}>
          {t("Cancel")}
        </Button>,
        <Button
          loading={isLoading}
          key="submit"
          type="primary"
          onClick={handleSubmitForm}
          disabled={isDisabledSubmit}
        >
          {!isClone ? t("Update") : t("Clone")}
        </Button>,
      ]}
    >
      {errors ? (
        <AlertError error={errors as ErrorObj} skipFields={["status", "comment", "attributes"]} />
      ) : null}

      <Form id="test-result-edit-form" layout="vertical" onFinish={handleSubmitForm}>
        <Row>
          <Col flex="1 0">
            <Form.Item
              label={t("Status")}
              validateStatus={errors?.status ? "error" : ""}
              help={errors?.status ? errors.status : "Set the test status (passed, failed etc.)."}
            >
              <Controller
                name="status"
                control={control}
                render={({ field }) => {
                  return (
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <Select
                        {...field}
                        placeholder={t("Please select")}
                        style={{ width: "100%" }}
                        id={`${isClone ? "clone" : "edit"}-result-status`}
                      >
                        {statuses.map((status) => (
                          <Select.Option key={status.id} value={Number(status.id)}>
                            <Status
                              name={status.name}
                              color={status.color}
                              id={status.id}
                              extraId={`${isClone ? "clone" : "edit"}-result`}
                            />
                          </Select.Option>
                        ))}
                      </Select>
                      <ApplyToStepsButton
                        steps={testResult.steps_results}
                        status={field.value}
                        onApply={handleStepsChange}
                      />
                    </div>
                  )
                }}
              />
            </Form.Item>

            <Form.Item
              label={t("Comment")}
              validateStatus={errors?.comment ? "error" : ""}
              help={errors?.comment ? errors.comment : ""}
            >
              <Controller
                name="comment"
                control={control}
                render={({ field }) => (
                  <TextAreaWithAttach
                    uploadId={`${isClone ? "clone" : "edit"}-result-comment`}
                    textAreaId={`${isClone ? "clone" : "edit"}-result-comment-textarea`}
                    fieldProps={field}
                    stateAttachments={{ attachments, setAttachments }}
                    customRequest={handleAttachmentsLoad}
                    setValue={setValue}
                  />
                )}
              />
            </Form.Item>
            <Attachment.DropFiles
              attachments={attachments}
              attachmentsIds={attachmentsIds}
              onChange={handleAttachmentsChange}
              onLoad={handleAttachmentsLoad}
              onRemove={handleAttachmentsRemove}
              register={register}
              idInput={`${isClone ? "clone" : "edit"}-result-attachments-input`}
            />
          </Col>
          <Col>
            <Divider type="vertical" style={{ height: "100%" }} />
          </Col>
          <Col flex="1 0">
            {!!testCase.steps.length && (
              <Row style={{ flexDirection: "column", marginTop: 0 }}>
                <div className="ant-col ant-form-item-label">
                  <label title="Steps">{t("Steps")}</label>
                </div>
                <Steps.ResultInEditModal
                  stepResultsData={testResult.steps_results}
                  stepResults={watchSteps}
                  setStepsResult={handleStepsChange}
                  id={`${isClone ? "clone" : "edit"}`}
                />
              </Row>
            )}
            <Controller
              name="attributes"
              control={control}
              render={({ field }) => (
                <Row style={{ flexDirection: "column", marginTop: testCase.steps.length ? 24 : 0 }}>
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
      </Form>
    </Modal>
  )
}
