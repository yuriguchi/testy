import { EditOutlined } from "@ant-design/icons"
import { Button, Form, Input, Modal, Switch, Tooltip, notification } from "antd"
import { useEffect, useState } from "react"
import { Controller, SubmitHandler, useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"

import { useUpdateProjectJsonMutation } from "entities/project/api"

import { config } from "shared/config"
import { ErrorObj, useErrors } from "shared/hooks"
import { AlertError, AlertSuccessChange } from "shared/ui"

interface Props {
  project: Project
}

interface ErrorData {
  is_result_editable?: string
  result_edit_limit?: string
}

export const EditTestResultsSettings = ({ project }: Props) => {
  const { t } = useTranslation()
  const [errors, setErrors] = useState<ErrorData | null>(null)
  const { onHandleError } = useErrors<ErrorData>(setErrors)
  const [isShow, setIsShow] = useState(false)
  const [updateProject, { isLoading }] = useUpdateProjectJsonMutation()

  const {
    handleSubmit,
    reset,
    control,
    setValue,
    watch,
    formState: { isDirty },
  } = useForm<ProjectSettings>()
  const isEditableValue = watch("is_result_editable")

  useEffect(() => {
    if (!project.settings) {
      return
    }

    setValue("is_result_editable", project.settings.is_result_editable)
    setValue("result_edit_limit", project.settings.result_edit_limit?.toString() ?? "")
  }, [isShow, project])

  const onSubmit: SubmitHandler<ProjectSettings> = async ({
    is_result_editable,
    result_edit_limit,
  }) => {
    setErrors(null)
    try {
      const settings: ProjectSettings = {
        is_result_editable,
        result_edit_limit:
          is_result_editable && result_edit_limit?.trim() ? result_edit_limit.trim() : null,
      }

      await updateProject({ id: project.id, body: { settings } }).unwrap()

      onCloseModal()
      notification.success({
        message: t("Success"),
        closable: true,
        description: (
          <AlertSuccessChange
            action="updated"
            title={t("Project test results settings")}
            link={`/administration/projects/${project.id}/settings`}
            id={project.id.toString()}
          />
        ),
      })
    } catch (err) {
      onHandleError(err)
    }
  }

  const onCloseModal = () => {
    setIsShow(false)
    setErrors(null)
    reset()
  }

  return (
    <>
      <Button type="default" icon={<EditOutlined />} onClick={() => setIsShow(true)}>
        {t("Edit")}
      </Button>
      <Modal
        className="edit-test-results-settings-modal"
        title={t("Edit project test results settings")}
        open={isShow}
        onCancel={() => setIsShow(false)}
        width="600px"
        centered
        footer={[
          <Button id="close-edit-test-results-settings" key="back" onClick={onCloseModal}>
            {t("Close")}
          </Button>,
          <Button
            id="edit-test-results-settings"
            loading={isLoading}
            key="submit"
            onClick={handleSubmit(onSubmit)}
            type="primary"
            disabled={!isDirty}
          >
            {t("Save")}
          </Button>,
        ]}
      >
        <>
          {errors ? (
            <AlertError
              error={errors as ErrorObj}
              skipFields={["is_result_editable", "result_edit_limit"]}
            />
          ) : null}
          <Form
            id="edit-test-results-settings-form"
            layout="vertical"
            onFinish={handleSubmit(onSubmit)}
          >
            <Form.Item
              label={t("Is Editable")}
              validateStatus={errors?.is_result_editable ? "error" : ""}
              help={errors?.is_result_editable ? errors.is_result_editable : ""}
            >
              <Controller
                name="is_result_editable"
                control={control}
                render={({ field }) => <Switch checked={isEditableValue} {...field} />}
              />
            </Form.Item>
            {isEditableValue && (
              <Form.Item
                label={
                  <Tooltip overlayStyle={{ minWidth: 460 }} title={config.estimateTooltip}>
                    {t("Edit time")}
                  </Tooltip>
                }
                validateStatus={errors?.result_edit_limit ? "error" : ""}
                help={errors?.result_edit_limit ? errors.result_edit_limit : ""}
              >
                <Controller
                  name="result_edit_limit"
                  control={control}
                  render={({ field }) => <Input {...field} value={field.value ?? ""} />}
                />
              </Form.Item>
            )}
          </Form>
        </>
      </Modal>
    </>
  )
}
