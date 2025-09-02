import { PlusOutlined } from "@ant-design/icons"
import { Button } from "antd"
import { useState } from "react"
import { useTranslation } from "react-i18next"

import { CreateProjectModal } from "./create-project-modal"

export const CreateProject = () => {
  const { t } = useTranslation()
  const [isShow, setIsShow] = useState(false)

  const handleClick = () => {
    setIsShow(true)
  }

  return (
    <>
      <Button id="create-project" icon={<PlusOutlined />} type="primary" onClick={handleClick}>
        {t("Create")} {t("Project")}
      </Button>
      <CreateProjectModal isShow={isShow} setIsShow={setIsShow} />
    </>
  )
}
