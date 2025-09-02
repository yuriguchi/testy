import { EditOutlined, PlusOutlined } from "@ant-design/icons"
import { Button, Form, Input, Modal, Select } from "antd"
import { Controller } from "react-hook-form"
import { useTranslation } from "react-i18next"

import { customAttributeTypes } from "shared/config/custom-attribute-types"
import { ErrorObj } from "shared/hooks"
import { AlertError } from "shared/ui"

import { SelectContentTypes } from "./ui"
import { PropsChangeCustomAttribute, useChangeCustomAttribute } from "./use-change-custom-attribute"

export const ChangeCustomAttribute = (props: PropsChangeCustomAttribute) => {
  const { t } = useTranslation()
  const {
    isShow,
    control,
    isDirty,
    isLoading,
    errors,
    contentTypes,
    handleClose,
    handleSubmitForm,
    handleShow,
  } = useChangeCustomAttribute(props)

  const { formType, attribute } = props
  const isCreate = formType === "create"
  const title = isCreate ? t("Create") : t("Edit")
  const titleBtn = isCreate ? t("Create") : t("Update")

  return (
    <>
      <Button
        id={isCreate ? "create-custom-attribute" : `${formType}-custom-attribute-${attribute?.id}`}
        icon={isCreate ? <PlusOutlined /> : <EditOutlined />}
        type={isCreate ? "primary" : undefined}
        style={isCreate ? { marginBottom: 16, float: "right" } : undefined}
        shape={isCreate ? "default" : "circle"}
        onClick={handleShow}
      >
        {isCreate ? t("Create Custom Attribute") : ""}
      </Button>
      <Modal
        className={`${formType}-custom-attribute-modal`}
        title={`${title} ${t("Custom Attribute")}`}
        open={isShow}
        onCancel={handleClose}
        width="600px"
        centered
        destroyOnClose
        footer={[
          <Button id={`close-${formType}-attribute`} key="back" onClick={handleClose}>
            {t("Close")}
          </Button>,
          <Button
            id={`${formType}-custom-attribute`}
            loading={isLoading}
            key="submit"
            onClick={handleSubmitForm}
            type="primary"
            disabled={!isDirty}
          >
            {titleBtn}
          </Button>,
        ]}
      >
        <>
          {errors ? (
            <AlertError
              error={errors as ErrorObj}
              skipFields={["name", "content_types", "applied_to"]}
            />
          ) : null}

          <Form id={`${formType}-attribute-form`} layout="vertical" onFinish={handleSubmitForm}>
            <Form.Item
              label={t("Name")}
              validateStatus={errors?.name ? "error" : ""}
              help={errors?.name ? errors.name : ""}
              required
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
              required
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
                    options={customAttributeTypes}
                  />
                )}
              />
            </Form.Item>
            <Form.Item
              label={t("Applied To")}
              validateStatus={errors?.applied_to ? "error" : ""}
              help={errors?.applied_to ? errors.applied_to : ""}
              required
            >
              <Controller
                name="applied_to"
                control={control}
                render={({ field }) => (
                  <SelectContentTypes
                    contentTypes={contentTypes}
                    value={field.value}
                    onChange={field.onChange}
                  />
                )}
              />
            </Form.Item>
          </Form>
        </>
      </Modal>
    </>
  )
}
