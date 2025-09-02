import { DeleteOutlined } from "@ant-design/icons"
import { Button } from "antd"
import { useState } from "react"
import { useTranslation } from "react-i18next"

import { DeleteProjectModal } from "./delete-project-modal"

export const DeleteProject = ({ project }: { project: Project }) => {
  const { t } = useTranslation()
  const [isShow, setIsShow] = useState(false)
  return (
    <>
      <Button id="delete-project" icon={<DeleteOutlined />} danger onClick={() => setIsShow(true)}>
        {t("Delete")}
      </Button>
      <DeleteProjectModal isShow={isShow} setIsShow={setIsShow} project={project} />
    </>
  )
}
