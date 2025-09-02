import { PlusOutlined } from "@ant-design/icons"
import { Button } from "antd"
import { useState } from "react"
import { useTranslation } from "react-i18next"

import { CreateEditLabelModal } from "../create-edit-label-modal/create-edit-label-modal"

export const CreateLabelButton = () => {
  const { t } = useTranslation()
  const [isShow, setIsShow] = useState(false)

  const handleShow = () => {
    setIsShow(true)
  }

  return (
    <>
      <Button
        id="create-label-button"
        type="primary"
        icon={<PlusOutlined />}
        onClick={handleShow}
        style={{ marginBottom: 16, float: "right" }}
      >
        {t("Create")} {t("Label")}
      </Button>
      <CreateEditLabelModal mode="create" isShow={isShow} setIsShow={setIsShow} />
    </>
  )
}
