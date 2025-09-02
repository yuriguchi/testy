import { PlusOutlined } from "@ant-design/icons"
import { Button } from "antd"
import { useAdministrationStatusModal } from "entities/status/model"
import { useTranslation } from "react-i18next"

import { StatusCreateEditModal } from "../status-create-edit-modal/status-create-edit-modal"

export const CreateStatusButton = () => {
  const { t } = useTranslation()
  const statusModal = useAdministrationStatusModal()
  const handleCreateClick = () => {
    statusModal.handleModalOpen({ mode: "create" })
  }

  return (
    <>
      <Button
        id="create-status"
        type="primary"
        icon={<PlusOutlined />}
        onClick={handleCreateClick}
        style={{ marginBottom: 16, float: "right" }}
      >
        {t("Create status")}
      </Button>
      {statusModal.isShow && <StatusCreateEditModal data={statusModal} />}
    </>
  )
}
