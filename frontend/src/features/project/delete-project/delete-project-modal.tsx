import { notification } from "antd"
import { useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"

import { useDeleteProjectMutation, useGetProjectDeletePreviewQuery } from "entities/project/api"

import { initInternalError } from "shared/libs"
import { AlertSuccessChange } from "shared/ui"

import { ModalConfirmDeleteArchive } from "widgets/[ui]/modal-confirm-delete-archive"

interface Props {
  isShow: boolean
  setIsShow: (isShow: boolean) => void
  project: Project
}

export const DeleteProjectModal = ({ isShow, setIsShow, project }: Props) => {
  const { t } = useTranslation()

  const navigate = useNavigate()
  const [deleteProject, { isLoading: isLoadingDelete }] = useDeleteProjectMutation()
  const { data, isLoading, status } = useGetProjectDeletePreviewQuery(String(project.id), {
    skip: !isShow,
  })

  const handleClose = () => {
    setIsShow(false)
  }

  const handleDelete = async () => {
    try {
      await deleteProject(Number(project.id)).unwrap()
      notification.success({
        message: t("Success"),
        closable: true,
        description: (
          <AlertSuccessChange id={String(project.id)} action="deleted" title="Project" />
        ),
      })
    } catch (err: unknown) {
      initInternalError(err)
    }

    navigate("/administration/projects")
    handleClose()
  }

  return (
    <ModalConfirmDeleteArchive
      status={status}
      isShow={isShow}
      isLoading={isLoading}
      isLoadingButton={isLoadingDelete}
      name={project.name}
      typeTitle={t("Project")}
      type="project"
      data={data ?? []}
      handleClose={handleClose}
      handleDelete={handleDelete}
      action="delete"
    />
  )
}
