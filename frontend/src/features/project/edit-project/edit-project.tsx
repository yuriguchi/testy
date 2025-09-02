import { EditOutlined } from "@ant-design/icons"
import { Button } from "antd"
import { useState } from "react"
import { useTranslation } from "react-i18next"

import { EditProjectModal } from "./edit-project-modal"

export const EditProject = ({ project }: { project: Project }) => {
  const { t } = useTranslation()
  const [isShow, setIsShow] = useState(false)

  const handleClick = () => {
    setIsShow(true)
  }

  return (
    <>
      <Button id="edit-project" icon={<EditOutlined />} onClick={handleClick}>
        {t("Edit")}
      </Button>
      <EditProjectModal isShow={isShow} setIsShow={setIsShow} project={project} />
    </>
  )
}
