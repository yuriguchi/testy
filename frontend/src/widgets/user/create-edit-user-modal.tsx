import { Button, Form, Input, Modal, Switch } from "antd"
import { Controller } from "react-hook-form"
import { useTranslation } from "react-i18next"

import { useUserModal } from "entities/user/model"

import { ErrorObj } from "shared/hooks"
import { AlertError } from "shared/ui"

export const CreateEditUserModal = () => {
  const { t } = useTranslation()
  const {
    title,
    isEditMode,
    isShow,
    isLoading,
    isActive,
    isAdmin,
    isDirty,
    errors,
    control,
    handleCancel,
    handleSubmitForm,
  } = useUserModal()
  const formType = isEditMode ? t("Edit").toLowerCase() : t("Create").toLowerCase()

  return (
    <Modal
      className={`${formType}-user-modal`}
      title={title}
      open={isShow}
      onCancel={handleCancel}
      width="600px"
      centered
      footer={[
        <Button id={`close-${formType}-user`} key="back" onClick={handleCancel}>
          {t("Close")}
        </Button>,
        <Button
          id={`${formType}-user-btn`}
          loading={isLoading}
          key="submit"
          onClick={handleSubmitForm}
          type="primary"
          disabled={!isDirty}
        >
          {isEditMode ? t("Update") : t("Create")}
        </Button>,
      ]}
    >
      <>
        {errors ? (
          <AlertError
            error={errors as ErrorObj}
            skipFields={[
              "username",
              "email",
              "password",
              "confirm",
              "first_name",
              "last_name",
              "is_active",
              "is_superuser",
            ]}
          />
        ) : null}

        <Form id={`${formType}-user-form`} layout="vertical" onFinish={handleSubmitForm}>
          <Form.Item
            label={t("Username")}
            validateStatus={errors?.username ? "error" : ""}
            help={errors?.username ? errors.username : ""}
            required={!isEditMode}
          >
            <Controller
              name="username"
              control={control}
              render={({ field }) => (
                <Input id={`${formType}-username`} {...field} disabled={isEditMode} />
              )}
            />
          </Form.Item>
          <Form.Item
            label={t("Email")}
            validateStatus={errors?.email ? "error" : ""}
            help={errors?.email ? errors.email : ""}
            required
          >
            <Controller
              name="email"
              control={control}
              render={({ field }) => <Input id={`${formType}-email`} {...field} />}
            />
          </Form.Item>
          {!isEditMode && (
            <>
              <Form.Item
                label={t("Password")}
                validateStatus={errors?.password ? "error" : ""}
                help={errors?.password ? errors.password : ""}
                required={!isEditMode}
              >
                <Controller
                  name="password"
                  control={control}
                  render={({ field }) => <Input.Password id={`${formType}-password`} {...field} />}
                />
              </Form.Item>
              <Form.Item
                name="confirm"
                label={t("Confirm Password")}
                dependencies={["password"]}
                validateStatus={errors?.confirm ? "error" : ""}
                help={errors?.confirm ? errors.confirm : ""}
                required={!isEditMode}
              >
                <Controller
                  name="confirm"
                  control={control}
                  render={({ field }) => <Input.Password id={`${formType}-confirm`} {...field} />}
                />
              </Form.Item>
            </>
          )}
          <Form.Item
            label={t("First Name")}
            validateStatus={errors?.first_name ? "error" : ""}
            help={errors?.first_name ? errors.first_name : ""}
          >
            <Controller
              name="first_name"
              control={control}
              render={({ field }) => <Input id={`${formType}-first-name`} {...field} />}
            />
          </Form.Item>
          <Form.Item
            label={t("Last Name")}
            validateStatus={errors?.last_name ? "error" : ""}
            help={errors?.last_name ? errors.last_name : ""}
          >
            <Controller
              name="last_name"
              control={control}
              render={({ field }) => <Input id={`${formType}-last-name`} {...field} />}
            />
          </Form.Item>
          <Form.Item
            label={t("Active")}
            validateStatus={errors?.is_active ? "error" : ""}
            help={errors?.is_active ? errors.is_active : ""}
          >
            <Controller
              name="is_active"
              control={control}
              render={({ field }) => (
                <Switch id={`${formType}-is-active`} checked={isActive} {...field} />
              )}
            />
          </Form.Item>
          <Form.Item
            label={t("Admin")}
            validateStatus={errors?.is_superuser ? "error" : ""}
            help={errors?.is_superuser ? errors.is_superuser : ""}
          >
            <Controller
              name="is_superuser"
              control={control}
              render={({ field }) => (
                <Switch id={`${formType}-is-admin`} checked={isAdmin} {...field} />
              )}
            />
          </Form.Item>
        </Form>
      </>
    </Modal>
  )
}
