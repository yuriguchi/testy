import { Button, Form, Modal } from "antd"
import { useContext } from "react"
import { useTranslation } from "react-i18next"

import { UserSearchInput } from "entities/user/ui"

import { ProjectContext } from "pages/project"

import styles from "./styles.module.css"
import { UpdateData } from "./use-assign-to-common"

interface Props {
  isOpenModal: boolean
  errors: Partial<UpdateData> | null
  isDirty: boolean
  isLoadingUpdateTest: boolean
  selectedUser: SelectData | undefined
  handleClose: () => void
  handleOpenAssignModal: () => void
  handleSubmitForm: () => void
  handleAssignUserChange: (data?: SelectData) => void
  handleAssignUserClear: () => void
  handleAssignToMe: () => void
  isAssignToMe: boolean
}

export const AssingToModal = ({
  isOpenModal,
  errors,
  isDirty,
  isLoadingUpdateTest,
  selectedUser,
  handleClose,
  handleSubmitForm,
  handleAssignUserChange,
  handleAssignUserClear,
  handleAssignToMe,
  isAssignToMe,
}: Props) => {
  const { t } = useTranslation()
  const { project } = useContext(ProjectContext)!

  return (
    <Modal
      className="test-assign-to-modal"
      title={t("Assign To")}
      open={isOpenModal}
      onCancel={handleClose}
      footer={[
        <Button key="back" onClick={handleClose}>
          {t("Cancel")}
        </Button>,
        <Button
          key="submit"
          type="primary"
          onClick={handleSubmitForm}
          disabled={!isDirty && !!selectedUser}
          loading={isLoadingUpdateTest}
        >
          {t("Save")}
        </Button>,
      ]}
    >
      <Form id="test-assign-form" layout="vertical" onFinish={handleSubmitForm}>
        <Form.Item
          label={t("Name")}
          validateStatus={errors?.assignUserId ? "error" : ""}
          help={errors?.assignUserId ?? ""}
        >
          <UserSearchInput
            selectedUser={selectedUser}
            handleChange={handleAssignUserChange}
            handleClear={handleAssignUserClear}
            project={project}
          />
          {!isAssignToMe && (
            <button className={styles.assignToMeModal} onClick={handleAssignToMe} type="button">
              {t("Assign To Me")}
            </button>
          )}
        </Form.Item>
      </Form>
    </Modal>
  )
}
