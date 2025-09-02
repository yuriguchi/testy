import { Button, Flex, Space, Typography } from "antd"
import { useTranslation } from "react-i18next"

import { icons } from "shared/assets/inner-icons"

import styles from "./styles.module.css"

const { ArrowLeftIcon } = icons

interface Props {
  model: "test-case" | "test-plan" | "test-suite" | "test-result"
  title: React.ReactNode
  type: "create" | "edit"
  onClose?: () => void
  onSubmit?: () => void
  submitNode?: React.ReactNode
  isLoadingSubmit?: boolean
  isDisabledSubmit?: boolean
}

export const FormViewHeader = ({
  model,
  title,
  type,
  isLoadingSubmit,
  isDisabledSubmit,
  submitNode,
  onClose,
  onSubmit,
}: Props) => {
  const { t } = useTranslation()
  const submitTitle = type === "create" ? t("Create") : t("Save")
  return (
    <Flex align="center" justify="space-between">
      <Flex align="center">
        {onClose && (
          <button className={styles.backBtn} type="button" onClick={onClose}>
            <ArrowLeftIcon width={40} height={40} />
          </button>
        )}
        <Typography.Title
          level={2}
          className={styles.title}
          data-testid={`${type}-${model}-title-view`}
        >
          {title}
        </Typography.Title>
      </Flex>
      <Space>
        {onClose && (
          <Button id={`${type}-${model}-cancel-btn`} key="back" onClick={onClose} size="large">
            {t("Cancel")}
          </Button>
        )}
        {onSubmit && !submitNode && (
          <Button
            id={`${type}-${model}-submit-btn`}
            key="submit"
            loading={isLoadingSubmit}
            onClick={onSubmit}
            type="primary"
            htmlType="submit"
            disabled={isDisabledSubmit}
            size="large"
          >
            {submitTitle}
          </Button>
        )}
        {submitNode}
      </Space>
    </Flex>
  )
}
