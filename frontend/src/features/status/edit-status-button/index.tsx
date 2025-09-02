import { EditOutlined } from "@ant-design/icons"
import { Button } from "antd"
import { useAdministrationStatusModal } from "entities/status/model"
import { useEffect } from "react"

import { StatusCreateEditModal } from "../status-create-edit-modal/status-create-edit-modal"

interface Props {
  record: Status
  onDisableTable?: (value: boolean) => void
}

export const EditStatusButton = ({ record, onDisableTable }: Props) => {
  const statusModal = useAdministrationStatusModal()

  useEffect(() => {
    onDisableTable?.(statusModal.isShow)
  }, [statusModal.isShow])

  return (
    <>
      <Button
        id={`${record.name}-edit`}
        icon={<EditOutlined />}
        shape="circle"
        onClick={() => statusModal.handleModalOpen({ status: record, mode: "edit" })}
      />
      {statusModal.isShow && <StatusCreateEditModal data={statusModal} />}
    </>
  )
}
