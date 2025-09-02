import { notification } from "antd"
import { useStatuses } from "entities/status/model/use-statuses"
import { useContext, useEffect, useState } from "react"
import { SubmitHandler, useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"
import { useParams } from "react-router-dom"

import { useAttachments } from "entities/attachment/model"

import { useCreateResultMutation, useUpdateResultMutation } from "entities/result/api"
import { useAttributesTestResult } from "entities/result/model"

import { ProjectContext } from "pages/project"

import { useErrors, useShowModalCloseConfirm } from "shared/hooks"
import { makeAttributesJson } from "shared/libs"
import { AlertSuccessChange } from "shared/ui"

import { filterAttributesByStatus } from "../utils"

interface ErrorData {
  status?: string
  comment?: string
  attributes?: string | null
}

interface UseEditResultModalProps {
  isShow: boolean
  setIsShow: React.Dispatch<React.SetStateAction<boolean>>
  testResult: Result
  isClone: boolean
  onSubmit?: (newResult: Result, oldResult: Result) => void
}

export const useEditCloneResultModal = ({
  setIsShow,
  testResult,
  isShow,
  isClone,
  onSubmit: onSubmitCb,
}: UseEditResultModalProps) => {
  const { t } = useTranslation()
  const { project } = useContext(ProjectContext)!
  const { showModal } = useShowModalCloseConfirm()
  const [errors, setErrors] = useState<ErrorData | null>(null)
  const {
    handleSubmit,
    reset,
    control,
    setValue,
    register,
    formState: { isDirty },
    watch,
  } = useForm<ResultFormData>({
    mode: "all",
    defaultValues: {
      comment: testResult.comment,
      status: testResult.status,
      attributes: [],
      steps: {},
      attachments: [],
    },
  })
  const watchStatus = watch("status")
  const watchSteps = watch("steps") ?? {}

  const { testPlanId } = useParams<ParamTestPlanId>()
  const { statuses, getStatusById, defaultStatus } = useStatuses({ project: project.id })
  const {
    setAttachments,
    onReset,
    onRemove,
    onLoad,
    onChange,
    removeAttachmentIds,
    attachments,
    attachmentsIds,
    isLoading: isLoadingCreateAttachment,
  } = useAttachments<ResultFormData>(control, project.id)
  const { onHandleError } = useErrors<ErrorData>(setErrors)
  const [updatedTestResult, { isLoading: isLoadingUpdateTestResult }] = useUpdateResultMutation()
  const [createResult, { isLoading: isLoadingCreateTestResult }] = useCreateResultMutation()
  const isLoading =
    isLoadingUpdateTestResult || isLoadingCreateTestResult || isLoadingCreateAttachment

  const {
    attributes: allAttributes,
    isLoading: isLoadingAttributes,
    setAttributes,
    addAttribute,
    onAttributeChangeName,
    onAttributeChangeType,
    onAttributeChangeValue,
    onAttributeRemove,
    getAttributeJson,
  } = useAttributesTestResult({ mode: "edit", setValue })

  const attributes = filterAttributesByStatus(allAttributes, statuses, watchStatus)

  const isStatusAvailable = (status: number) => !!getStatusById(status)

  useEffect(() => {
    if (!isShow) return
    const resultSteps: Record<string, number> = {}
    testResult.steps_results.forEach((result) => {
      const stepId = String(result.id)
      if (isStatusAvailable(result.status)) {
        resultSteps[stepId] = result.status
      }
    })

    const testResultAttachesWithUid = testResult.attachments.map((attach) => ({
      ...attach,
      uid: String(attach.id),
    }))
    if (testResultAttachesWithUid.length && !isClone) {
      setAttachments(testResultAttachesWithUid)
    }

    const attrs = getAttributeJson(testResult.attributes)
    setAttributes(attrs)

    reset({
      comment: testResult.comment,
      status: getStatusById(testResult.status) ? testResult.status : undefined,
      attributes: attrs,
      steps: resultSteps,
      attachments: testResult.attachments.map((i) => i.id),
    })
  }, [isShow, isClone, testResult, statuses])

  useEffect(() => {
    if (isLoadingAttributes) return

    const shouldSetDefaultStatus = defaultStatus && !watchStatus && isShow
    if (shouldSetDefaultStatus) {
      setValue("status", defaultStatus.id, { shouldDirty: true })

      const newSteps = testResult.steps_results.reduce(
        (acc, result) => {
          if (result.id) {
            acc[result.id] = isStatusAvailable(result.status) ? result.status : defaultStatus.id
          }
          return acc
        },
        {} as Record<string, number>
      )

      reset({
        comment: testResult.comment,
        status: testResult.status,
        attributes: getAttributeJson(testResult.attributes),
        steps: newSteps,
      })
    }
  }, [defaultStatus, isShow, watchStatus, testResult.steps_results, isLoadingAttributes])

  const onCloseModal = () => {
    setIsShow(false)
    setErrors(null)
    reset()
    removeAttachmentIds()
    setAttributes([])
    onReset()
  }

  const handleCancel = () => {
    if (isLoading) return

    if (isDirty) {
      showModal(onCloseModal)
      return
    }

    onCloseModal()
  }

  const onSubmit: SubmitHandler<ResultFormData> = async (data) => {
    if (!testResult) return
    setErrors(null)

    const { isSuccess, attributesJson, errors: attributesErrors } = makeAttributesJson(attributes)

    if (!isSuccess) {
      setErrors({ attributes: JSON.stringify(attributesErrors) })
      return
    }

    const stepsResultData: { id: string; status: number }[] = []

    if (Object.keys(watchSteps).length) {
      Object.entries(watchSteps).forEach(([id, status]) => {
        stepsResultData.push({ id, status })
      })
    }

    try {
      const dataReq = {
        ...data,
        attributes: attributesJson,
        steps_results: stepsResultData,
        test: testResult.test,
      }
      let newResult = null
      if (!isClone) {
        newResult = await updatedTestResult({
          id: testResult.id,
          testPlanId: testPlanId ? Number(testPlanId) : null,
          body: dataReq as ResultUpdate,
        }).unwrap()
      } else {
        const findStep = (id: string) =>
          testResult.steps_results.find((i) => i.id === parseInt(id))?.step
        const stepsResultCreate = stepsResultData
          .map((i) => {
            return { step: findStep(i.id)?.toString(), status: i.status }
          })
          .filter((i) => i.step !== undefined) as StepResultCreate[]
        newResult = await createResult({
          testPlanId: testPlanId ? Number(testPlanId) : null,
          body: { ...dataReq, steps_results: stepsResultCreate } as ResultCreate,
        }).unwrap()
      }
      onCloseModal()

      notification.success({
        message: t("Success"),
        closable: true,
        description: (
          <AlertSuccessChange
            action="updated"
            title={t("Result")}
            link={`/projects/${project.id}/plans/${testPlanId}/?test=${newResult.test}#result-${newResult.id}`}
            id={String(newResult.id)}
          />
        ),
      })
      onSubmitCb?.(newResult, testResult)
    } catch (err: unknown) {
      onHandleError(err)
    }
  }

  const handleStepsChange = (stepsResult: Record<string, number>) => {
    setValue("steps", stepsResult, { shouldDirty: true })
  }

  const isAllStepsSelected = testResult.steps_results.every((result) => watchSteps[result.id])
  const isDisabledSubmit = (!isDirty && !isClone) || !isAllStepsSelected || !watchStatus

  return {
    isLoading,
    errors,
    control,
    attachments,
    attachmentsIds,
    watchSteps,
    isDirty,
    setAttachments,
    handleStepsChange,
    handleAttachmentsChange: onChange,
    handleAttachmentsLoad: onLoad,
    handleAttachmentsRemove: onRemove,
    setValue,
    handleCancel,
    register,
    attributes,
    setAttributes,
    addAttribute,
    onAttributeChangeType,
    onAttributeChangeValue,
    onAttributeChangeName,
    onAttributeRemove,
    handleSubmitForm: handleSubmit(onSubmit),
    statuses,
    isDisabledSubmit,
  }
}
