import { notification } from "antd"
import { useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"

import { useDeleteTestSuiteMutation, useGetSuiteDeletePreviewQuery } from "entities/suite/api"

import { initInternalError } from "shared/libs"
import { AlertSuccessChange } from "shared/ui"

import { ModalConfirmDeleteArchive } from "widgets/[ui]/modal-confirm-delete-archive"

interface Props {
  isShow: boolean
  setIsShow: (isShow: boolean) => void
  testSuite: Suite
  onSubmit?: (suite: Suite) => void
}

export const DeleteTestSuiteModal = ({ isShow, setIsShow, testSuite, onSubmit }: Props) => {
  const { t } = useTranslation()
  const [deleteTestSuite, { isLoading: isLoadingDelete }] = useDeleteTestSuiteMutation()
  const { data, isLoading, status } = useGetSuiteDeletePreviewQuery(String(testSuite.id), {
    skip: !isShow,
  })
  const navigate = useNavigate()

  const handleClose = () => {
    setIsShow(false)
  }

  const handleDelete = async () => {
    try {
      await deleteTestSuite(testSuite.id).unwrap()
      navigate(`/projects/${testSuite.project}/suites`)
      notification.success({
        message: t("Success"),
        closable: true,
        description: (
          <AlertSuccessChange id={String(testSuite.id)} action="deleted" title={t("Test Suite")} />
        ),
      })
      onSubmit?.(testSuite)
    } catch (err: unknown) {
      initInternalError(err)
    }
  }

  return (
    <ModalConfirmDeleteArchive
      status={status}
      isShow={isShow}
      isLoading={isLoading}
      isLoadingButton={isLoadingDelete}
      name={testSuite.name}
      typeTitle={t("Test Suite")}
      type="test-suite"
      data={data ?? []}
      handleClose={handleClose}
      handleDelete={handleDelete}
      action="delete"
    />
  )
}
