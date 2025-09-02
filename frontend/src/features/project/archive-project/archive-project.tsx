import { Dropdown, MenuProps } from "antd"
import { useState } from "react"
import { useTranslation } from "react-i18next"

import { DeleteProject } from "../delete-project/delete-project"
import { ArchiveProjectModal } from "./archive-project-modal"

export const ArchiveProject = ({ project }: { project: Project }) => {
  const { t } = useTranslation()
  const [isShow, setIsShow] = useState(false)

  const items: MenuProps["items"] = [
    {
      key: "1",
      label: <DeleteProject project={project} />,
    },
  ]

  return (
    <>
      <Dropdown.Button
        className="archive-project"
        menu={{ items }}
        danger
        onClick={() => setIsShow(true)}
      >
        {t("Archive")}
      </Dropdown.Button>
      <ArchiveProjectModal isShow={isShow} setIsShow={setIsShow} project={project} />
    </>
  )
}
