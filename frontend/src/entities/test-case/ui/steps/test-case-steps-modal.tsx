import { Button, Form, Input, Modal } from "antd"
import { Controller } from "react-hook-form"
import { useTranslation } from "react-i18next"

import {
  TestCaseStepsModalProps,
  useTestCaseStepsModal,
} from "entities/test-case/model/use-test-case-steps-modal"

import { Attachment, TextAreaWithAttach } from "shared/ui"

export const TestCaseStepsModal = ({
  step,
  isEdit,
  onSubmit,
  onCloseModal,
}: TestCaseStepsModalProps) => {
  const { t } = useTranslation()
  const {
    isLoading,
    isDirty,
    errors,
    control,
    attachments,
    attachmentsIds,
    handleClose,
    handleSubmit,
    onSubmitForm,
    onLoad,
    setAttachments,
    setValue,
    onChange,
    register,
    onRemove,
  } = useTestCaseStepsModal({ step, isEdit, onSubmit, onCloseModal })

  return (
    <Modal
      className="test-case-steps-modal"
      title={`${isEdit ? t("Edit") : t("Create")} ${t("step")}`}
      open={!!step}
      onCancel={handleClose}
      centered
      footer={[
        <Button id="modal-steps-cancel-btn" key="back" onClick={handleClose}>
          {t("Cancel")}
        </Button>,
        <Button
          id={isEdit ? "modal-steps-edit-btn" : "modal-steps-create-btn"}
          key="submit"
          type="primary"
          onClick={handleSubmit(onSubmitForm)}
          loading={isLoading}
          disabled={!isDirty}
        >
          {isEdit ? t("Update") : t("Create")}
        </Button>,
      ]}
    >
      <Form id="test-case-steps-form" layout="vertical" onFinish={handleSubmit(onSubmitForm)}>
        <Form.Item
          label={t("Name")}
          validateStatus={errors?.name ? "error" : ""}
          help={errors?.name?.message ?? ""}
          required
        >
          <Controller
            name="name"
            control={control}
            rules={{
              maxLength: { value: 255, message: t("Maximum length 255") },
              required: { value: true, message: t("Required field") },
            }}
            render={({ field }) => <Input {...field} data-testid="test-case-steps-name-input" />}
          />
        </Form.Item>
        <Form.Item
          label={t("Scenario")}
          validateStatus={errors?.scenario ? "error" : ""}
          help={errors.scenario?.message ?? ""}
          required
        >
          <Controller
            name="scenario"
            control={control}
            render={() => (
              <Controller
                name="scenario"
                control={control}
                rules={{
                  required: { value: true, message: t("Required field") },
                }}
                render={({ field }) => (
                  <TextAreaWithAttach
                    uploadId="step-scenario"
                    fieldProps={field}
                    stateAttachments={{ attachments, setAttachments }}
                    customRequest={onLoad}
                    setValue={setValue}
                  />
                )}
              />
            )}
          />
        </Form.Item>
        <Form.Item
          label={t("Expected")}
          validateStatus={errors?.expected ? "error" : ""}
          help={errors?.expected?.message ?? ""}
        >
          <Controller
            name="expected"
            control={control}
            render={({ field }) => (
              <TextAreaWithAttach
                uploadId="step-expected"
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
          idInput="test-case-steps-attachments-input"
        />
      </Form>
    </Modal>
  )
}
