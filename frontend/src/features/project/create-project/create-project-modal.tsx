import { Button, Form, Input, Modal, Switch, Upload, notification } from "antd"
import { RcFile, UploadChangeParam, UploadFile } from "antd/lib/upload"
import { useState } from "react"
import { Controller, SubmitHandler, useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"

import { useCreateProjectMutation } from "entities/project/api"
import { ProjectIcon } from "entities/project/ui"

import { ErrorObj, useErrors, useShowModalCloseConfirm } from "shared/hooks"
import { fileReader } from "shared/libs"
import { AlertError, AlertSuccessChange } from "shared/ui"

const { TextArea } = Input

interface ErrorData {
  name?: string
  description?: string
  is_archive?: string
  is_private?: string
}

interface Props {
  isShow: boolean
  setIsShow: (isShow: boolean) => void
}

export const CreateProjectModal = ({ isShow, setIsShow }: Props) => {
  const { t } = useTranslation()
  const { showModal } = useShowModalCloseConfirm()
  const [errors, setErrors] = useState<ErrorData | null>(null)
  const {
    handleSubmit,
    reset,
    control,
    setValue,
    watch,
    formState: { isDirty },
  } = useForm<Project>({
    defaultValues: {
      name: "",
      description: "",
      icon: "",
      is_archive: false,
      is_private: false,
    },
  })
  const [createProject, { isLoading }] = useCreateProjectMutation()
  const { onHandleError } = useErrors<ErrorData>(setErrors)
  const [localIcon, setLocalIcon] = useState<string | null>(null)
  const nameWatch = watch("name")
  const isPrivate = watch("is_private")

  const onSubmit: SubmitHandler<Project> = async (data) => {
    setErrors(null)

    try {
      const fmData = new FormData()

      fmData.append("name", data.name)
      fmData.append("description", data.description)
      fmData.append("is_archive", String(data.is_archive))
      fmData.append("icon", data.icon ?? "")
      fmData.append("is_private", String(data.is_private))
      const newProject = await createProject(fmData).unwrap()

      onCloseModal()
      notification.success({
        message: t("Success"),
        closable: true,
        description: (
          <AlertSuccessChange
            action="created"
            title="Project"
            link={`/administration/projects/${newProject.id}/overview/`}
            id={String(newProject.id)}
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
    setLocalIcon(null)
    reset()
  }

  const handleCancel = () => {
    if (isLoading) return

    if (isDirty) {
      showModal(onCloseModal)
      return
    }

    onCloseModal()
  }

  const onChange = async (info: UploadChangeParam<UploadFile<unknown>>) => {
    if (!info.file.originFileObj) return
    const file = await fileReader(info.file)
    setLocalIcon(file.url)
    setValue("icon", file.file as unknown as string, {
      shouldDirty: true,
      shouldTouch: true,
    })
  }

  const beforeUpload = (file: RcFile) => {
    const isCorrectType = file.type === "image/png" || file.type === "image/jpeg"
    if (!isCorrectType) {
      notification.error({
        message: t("Error!"),
        description: `${file.name} ${t("is not a png or jpg file")}`,
      })
    }

    return isCorrectType || Upload.LIST_IGNORE
  }

  const handleDeleteIconClick = () => {
    setLocalIcon(null)
    setValue("icon", "", { shouldDirty: true, shouldTouch: true })
  }

  return (
    <Modal
      className="create-project-modal"
      title={`${t("Create")} ${t("Project")}`}
      open={isShow}
      onCancel={handleCancel}
      width="600px"
      centered
      footer={[
        <Button id="close-create-project" key="back" onClick={handleCancel}>
          {t("Close")}
        </Button>,
        <Button
          id="create-project"
          loading={isLoading}
          key="submit"
          onClick={handleSubmit(onSubmit)}
          type="primary"
          disabled={!isDirty}
        >
          {t("Create")}
        </Button>,
      ]}
    >
      <>
        {errors ? (
          <AlertError
            error={errors as ErrorObj}
            skipFields={["name", "description", "is_archive", "is_private"]}
          />
        ) : null}

        <Form id="create-edit-project-form" layout="vertical" onFinish={handleSubmit(onSubmit)}>
          <Form.Item label={t("Icon")}>
            <Controller
              name="icon"
              control={control}
              render={() => {
                return (
                  <div
                    style={{ display: "flex", alignItems: "center", flexDirection: "row", gap: 14 }}
                  >
                    <ProjectIcon
                      name={nameWatch || "T"}
                      icon={localIcon}
                      dataTestId="create-project-icon"
                    />
                    <Upload
                      name="avatar"
                      showUploadList={false}
                      onChange={onChange}
                      style={{ width: 180 }}
                      customRequest={() => {}}
                      beforeUpload={beforeUpload}
                      data-testid="create-project-upload-icon-input"
                    >
                      <Button size="middle" data-testid="create-project-upload-icon-button">
                        {t("Upload icon")}
                      </Button>
                    </Upload>
                    {localIcon && (
                      <Button
                        size="middle"
                        danger
                        onClick={handleDeleteIconClick}
                        data-testid="create-project-delete-icon-button"
                      >
                        {t("Delete icon")}
                      </Button>
                    )}
                  </div>
                )
              }}
            />
          </Form.Item>
          <Form.Item
            label={t("Name")}
            validateStatus={errors?.name ? "error" : ""}
            help={errors?.name ? errors.name : ""}
          >
            <Controller
              name="name"
              control={control}
              render={({ field }) => <Input {...field} data-testid="create-project-name" />}
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
                <TextArea rows={4} {...field} data-testid="create-project-description" />
              )}
            />
          </Form.Item>
          <Form.Item
            label={t("Private")}
            validateStatus={errors?.is_private ? "error" : ""}
            help={errors?.is_private ? errors.is_private : ""}
          >
            <Controller
              name="is_private"
              control={control}
              render={({ field }) => (
                <Switch checked={isPrivate} {...field} data-testid="create-project-is-private" />
              )}
            />
          </Form.Item>
        </Form>
      </>
    </Modal>
  )
}
