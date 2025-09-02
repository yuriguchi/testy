import { UnlockOutlined } from "@ant-design/icons"
import { Button, Form, Input, Modal, Tooltip, notification } from "antd"
import { useForm } from "antd/lib/form/Form"
import { useTranslation } from "react-i18next"

import { useRequestAccessMutation } from "entities/project/api"

import styles from "./styles.module.css"

interface Props {
  project: Project
  type?: "min" | "default"
}

export const RequestProjectAccess = ({ project, type = "default" }: Props) => {
  const { t } = useTranslation()
  const [form] = useForm<{ reason: string }>()
  const [requestAccess] = useRequestAccessMutation()

  const handleRequestAccess = () => {
    form.validateFields().then(async (values) => {
      try {
        const { reason } = values
        await requestAccess({ id: project.id, reason }).unwrap()
        notification.success({
          message: t("Success"),
          closable: true,
          description: t("Request has been sent"),
        })
      } catch (e) {
        notification.error({
          message: t("Error!"),
          closable: true,
          description: t("Failed to send a reqeust"),
        })
      }
    })
  }

  const TEXT = `${t("Request access to")} ${project.name}`
  const BUTTON = (
    <Button
      type="primary"
      block
      className={styles.requestBtn}
      icon={<UnlockOutlined />}
      style={{ width: "fit-content", padding: "5px 8px" }}
      onClick={() =>
        Modal.confirm({
          title: t("Request Access"),
          icon: null,
          content: (
            <Form form={form}>
              <Form.Item name="reason" label={t("Reason")}>
                <Input />
              </Form.Item>
            </Form>
          ),
          onOk: handleRequestAccess,
          cancelText: t("Cancel"),
          okText: t("Send"),
          okButtonProps: { "data-testid": "request-access-button-confirm" },
          cancelButtonProps: { "data-testid": "request-access-button-cancel" },
        })
      }
    >
      {type === "default" ? TEXT : null}
    </Button>
  )

  if (type === "default") return BUTTON
  return (
    <Tooltip title={TEXT} placement="top">
      {BUTTON}
    </Tooltip>
  )
}
