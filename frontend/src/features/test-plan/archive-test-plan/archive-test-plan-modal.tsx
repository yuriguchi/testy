import { notification } from "antd"
import { useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"

import {
  useArchiveTestPlanMutation,
  useGetTestPlanArchivePreviewQuery,
} from "entities/test-plan/api"

import { initInternalError } from "shared/libs"
import { AlertSuccessChange } from "shared/ui"

import { ModalConfirmDeleteArchive } from "widgets/[ui]/modal-confirm-delete-archive"

interface Props {
  isShow: boolean
  setIsShow: (toggle: boolean) => void
  testPlan: TestPlan
  onSubmit?: (plan: TestPlan) => void
}

export const ArchiveTestPlanModal = ({ isShow, setIsShow, testPlan, onSubmit }: Props) => {
  const { t } = useTranslation()
  const [archiveTestPlan, { isLoading: isLoadingDelete }] = useArchiveTestPlanMutation()
  const { data, isLoading, status } = useGetTestPlanArchivePreviewQuery(String(testPlan.id), {
    skip: !isShow,
  })

  const navigate = useNavigate()

  const handleClose = () => {
    setIsShow(false)
  }

  const handleArchive = async () => {
    try {
      await archiveTestPlan(testPlan.id).unwrap()
      navigate(`/projects/${testPlan.project}/plans`)
      notification.success({
        message: t("Success"),
        closable: true,
        description: (
          <AlertSuccessChange id={String(testPlan.id)} action="archived" title={t("Test Plan")} />
        ),
      })
      onSubmit?.(testPlan)
      handleClose()
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
      name={testPlan.name}
      typeTitle={t("Test Plan")}
      type="test-plan"
      data={data ?? []}
      handleClose={handleClose}
      handleDelete={handleArchive}
      action="archive"
    />
  )
}
