import { EditOutlined } from "@ant-design/icons"
import { Button } from "antd"
import { useState } from "react"

import { CreateEditLabelModal } from "../create-edit-label-modal/create-edit-label-modal"

interface Props {
  label: Label
}

export const EditLabelButton = ({ label }: Props) => {
  const [isShow, setIsShow] = useState(false)

  const handleShow = () => {
    setIsShow(true)
  }

  return (
    <>
      <Button
        id={`${label.name}-edit-label-button`}
        icon={<EditOutlined />}
        shape="circle"
        onClick={handleShow}
      />
      <CreateEditLabelModal mode="edit" label={label} isShow={isShow} setIsShow={setIsShow} />
    </>
  )
}
