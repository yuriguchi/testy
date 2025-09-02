import { DeleteOutlined } from "@ant-design/icons"
import { Button } from "antd"
import { useAdministrationStatusModal } from "entities/status/model"

import { StatusCreateEditModal } from "../status-create-edit-modal/status-create-edit-modal"

interface Props {
  record: Status
}

export const DeleteStatusButton = ({ record }: Props) => {
  const statusModal = useAdministrationStatusModal()
  return (
    <>
      <Button
        id={`${record.name}-delete`}
        icon={<DeleteOutlined />}
        shape="circle"
        danger
        onClick={() => statusModal.handleDeleteStatus(Number(record.id))}
      />
      {statusModal.isShow && <StatusCreateEditModal data={statusModal} />}
    </>
  )
}
