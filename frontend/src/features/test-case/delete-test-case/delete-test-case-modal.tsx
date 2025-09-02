import { notification } from "antd"
import { useTranslation } from "react-i18next"
import { useSearchParams } from "react-router-dom"

import { useAppDispatch } from "app/hooks"

import { useDeleteTestCaseMutation, useGetTestCaseDeletePreviewQuery } from "entities/test-case/api"
import { clearDrawerTestCase } from "entities/test-case/model"

import { initInternalError } from "shared/libs"
import { AlertSuccessChange } from "shared/ui"

import { ModalConfirmDeleteArchive } from "widgets/[ui]/modal-confirm-delete-archive"

interface Props {
  isShow: boolean
  setIsShow: (isShow: boolean) => void
  testCase: TestCase
  onSubmit?: (testCase: TestCase) => void
}

export const DeleteTestCaseModal = ({ isShow, setIsShow, testCase, onSubmit }: Props) => {
  const { t } = useTranslation()
  const [deleteTestCase, { isLoading: isLoadingDelete }] = useDeleteTestCaseMutation()
  const { data, isLoading, status } = useGetTestCaseDeletePreviewQuery(String(testCase.id), {
    skip: !isShow,
  })
  const [searchParams, setSearchParams] = useSearchParams()
  const dispatch = useAppDispatch()

  const handleClose = () => {
    setIsShow(false)
  }

  const handleDelete = async () => {
    try {
      searchParams.delete("test_case")
      searchParams.delete("version")
      setSearchParams(() => {
        dispatch(clearDrawerTestCase())
        return searchParams
      })
      await deleteTestCase(testCase.id).unwrap()
      notification.success({
        message: t("Success"),
        closable: true,
        description: (
          <AlertSuccessChange id={String(testCase.id)} action="deleted" title={t("Test Case")} />
        ),
      })
      onSubmit?.(testCase)
    } catch (err: unknown) {
      initInternalError(err)
    }

    handleClose()
  }

  return (
    <ModalConfirmDeleteArchive
      status={status}
      isShow={isShow}
      isLoading={isLoading}
      isLoadingButton={isLoadingDelete}
      name={testCase.name}
      typeTitle={t("Test Case")}
      type="test-case"
      data={data ?? []}
      handleClose={handleClose}
      handleDelete={handleDelete}
      action="delete"
    />
  )
}
