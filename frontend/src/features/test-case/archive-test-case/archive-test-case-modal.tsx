import { notification } from "antd"
import { useTranslation } from "react-i18next"
import { useSearchParams } from "react-router-dom"

import { useAppDispatch } from "app/hooks"

import {
  useArchiveTestCaseMutation,
  useGetTestCaseArchivePreviewQuery,
} from "entities/test-case/api"
import { clearDrawerTestCase } from "entities/test-case/model"

import { initInternalError } from "shared/libs"
import { AlertSuccessChange } from "shared/ui"

import { ModalConfirmDeleteArchive } from "widgets/[ui]"

interface Props {
  isShow: boolean
  setIsShow: (isShow: boolean) => void
  testCase: TestCase
  onSubmit?: (testCase: TestCase) => void
}

export const ArchiveTestCaseModal = ({ isShow, setIsShow, testCase, onSubmit }: Props) => {
  const { t } = useTranslation()
  const [archiveTestCase, { isLoading: isLoadingDelete }] = useArchiveTestCaseMutation()
  const { data, isLoading, status } = useGetTestCaseArchivePreviewQuery(String(testCase.id), {
    skip: !isShow,
  })
  const dispatch = useAppDispatch()
  const [searchParams, setSearchParams] = useSearchParams()

  const handleClose = () => {
    setIsShow(false)
  }

  const handleArchive = async () => {
    try {
      await archiveTestCase(testCase.id).unwrap()
      notification.success({
        message: t("Success"),
        closable: true,
        description: (
          <AlertSuccessChange id={String(testCase.id)} action="archived" title={t("Test Case")} />
        ),
      })
      searchParams.delete("test_case")
      searchParams.delete("version")
      setSearchParams(searchParams)
      dispatch(clearDrawerTestCase())
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
      handleDelete={handleArchive}
      action="archive"
    />
  )
}
