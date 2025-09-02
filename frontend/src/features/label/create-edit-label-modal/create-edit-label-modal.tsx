import { Button, Form, Input, Modal, Select } from "antd"
import { Controller } from "react-hook-form"
import { useTranslation } from "react-i18next"

import { labelTypes } from "shared/config/label-types"
import { ErrorObj } from "shared/hooks"
import { AlertError } from "shared/ui"

import {
  UseCreateEditLabelModalProps,
  useCreateEditLabelModal,
} from "./use-create-edit-label-modal"

export const CreateEditLabelModal = (props: UseCreateEditLabelModalProps) => {
  const { t } = useTranslation()
  const { title, isLoading, isDirty, control, errors, handleCancel, handleSubmitForm } =
    useCreateEditLabelModal(props)

  return (
    <Modal
      className={`${props.mode}-label-modal`}
      title={title}
      open={props.isShow}
      onCancel={handleCancel}
      width="600px"
      centered
      footer={[
        <Button id={`${props.mode}-label-close`} key="back" onClick={handleCancel}>
          {t("Close")}
        </Button>,
        <Button
          id={`${props.mode}-label-button`}
          loading={isLoading}
          key="submit"
          onClick={handleSubmitForm}
          type="primary"
          disabled={!isDirty}
        >
          {props.mode === "edit" ? t("Update") : t("Create")}
        </Button>,
      ]}
    >
      <>
        {errors ? <AlertError error={errors as ErrorObj} skipFields={["name"]} /> : null}

        <Form id={`${props.mode}-label-form`} layout="vertical" onFinish={handleSubmitForm}>
          <Form.Item
            label={t("Name")}
            validateStatus={errors?.name ? "error" : ""}
            help={errors?.name ? errors.name : ""}
          >
            <Controller
              name="name"
              control={control}
              render={({ field }) => <Input {...field} />}
            />
          </Form.Item>
          <Form.Item
            label={t("Type")}
            validateStatus={errors?.type ? "error" : ""}
            help={errors?.type ? errors.type : ""}
          >
            <Controller
              name="type"
              control={control}
              defaultValue={0}
              render={({ field }) => (
                <Select
                  {...field}
                  placeholder={t("Please select")}
                  style={{ width: "100%" }}
                  options={labelTypes}
                />
              )}
            />
          </Form.Item>
        </Form>
      </>
    </Modal>
  )
}
