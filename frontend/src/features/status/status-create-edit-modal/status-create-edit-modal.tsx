import { Button, ColorPicker, Form, Input, Modal } from "antd"
import { useAdministrationStatusModal } from "entities/status/model"
import { Controller } from "react-hook-form"
import { useTranslation } from "react-i18next"

import { ErrorObj } from "shared/hooks/use-alert-error"
import { AlertError } from "shared/ui"

interface Props {
  data: ReturnType<typeof useAdministrationStatusModal>
}

export const StatusCreateEditModal = ({ data }: Props) => {
  const { t } = useTranslation()
  const {
    title,
    isShow,
    mode,
    isLoading,
    errors,
    control,
    isDirty,
    handleCancel,
    handleSubmitForm,
  } = data
  return (
    <Modal
      className="create-edit-status-modal"
      title={title}
      open={isShow}
      onCancel={handleCancel}
      width="600px"
      centered
      footer={[
        <Button id="close-update-create-status" key="back" onClick={handleCancel}>
          {t("Close")}
        </Button>,
        <Button
          id="update-create-status"
          loading={isLoading}
          key="submit"
          onClick={handleSubmitForm}
          type="primary"
          disabled={!isDirty}
        >
          {mode === "edit" ? t("Update") : t("Create")}
        </Button>,
      ]}
    >
      <>
        {errors ? <AlertError error={errors as ErrorObj} skipFields={["name"]} /> : null}

        <Form layout="vertical" onFinish={handleSubmitForm} data-testid={`${mode}-status-form`}>
          <Form.Item
            label={t("Name")}
            validateStatus={errors?.name ? "error" : ""}
            help={errors?.name ? errors.name : ""}
          >
            <Controller
              name="name"
              control={control}
              render={({ field }) => <Input {...field} data-testid={`${mode}-status-name`} />}
            />
          </Form.Item>
          <Form.Item
            label={t("Color")}
            validateStatus={errors?.color ? "error" : ""}
            help={errors?.color ? errors.color : ""}
          >
            <Controller
              name="color"
              control={control}
              render={({ field }) => (
                <ColorPicker
                  value={field.value}
                  showText
                  format="rgb"
                  onChangeComplete={(color) => {
                    field.onChange(color.toRgbString())
                  }}
                  data-testid={`${mode}-status-color-picker-button`}
                />
              )}
            />
          </Form.Item>
        </Form>
      </>
    </Modal>
  )
}
