import { notification } from "antd"
import { useStatuses } from "entities/status/model/use-statuses"
import { useContext, useEffect, useState } from "react"
import { SubmitHandler, useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"
import { useParams } from "react-router-dom"

import { useAppSelector } from "app/hooks"

import { useAttachments } from "entities/attachment/model"

import { useCreateResultMutation } from "entities/result/api"
import { useAttributesTestResult } from "entities/result/model/use-attributes-test-result"

import { selectDrawerTest } from "entities/test/model"

import { ProjectContext } from "pages/project"

import { useErrors, useShowModalCloseConfirm } from "shared/hooks"
import { makeAttributesJson } from "shared/libs"
import { AlertSuccessChange } from "shared/ui"

import { filterAttributesByStatus } from "../utils"

export interface CreateResultModalProps {
  isShow: boolean
  setIsShow: React.Dispatch<React.SetStateAction<boolean>>
  testCase: TestCase
  onSubmit?: (result: Result) => void
}

interface ErrorData {
  status?: string
  comment?: string
  attributes?: string | null
}

export const useCreateResultModal = ({
  setIsShow,
  testCase,
  isShow,
  onSubmit: onSubmitCb,
}: CreateResultModalProps) => {
  const { t } = useTranslation()
  const { project } = useContext(ProjectContext)!
  const { showModal } = useShowModalCloseConfirm()
  const [errors, setErrors] = useState<ErrorData | null>(null)
  const [createResult, { isLoading }] = useCreateResultMutation()
  const {
    handleSubmit,
    reset,
    control,
    setValue,
    register,
    formState: { isDirty },
    watch,
  } = useForm<ResultFormData>({
    defaultValues: {
      comment: "",
      status: null,
      attachments: [],
      attributes: [],
      steps: {},
    },
  })
  const watchStatus = watch("status")
  const drawerTest = useAppSelector(selectDrawerTest)
  const { testPlanId } = useParams<ParamTestPlanId>()
  const { statuses, defaultStatus } = useStatuses({ project: project.id })
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

  const {
    attributes: allAttributes,
    addAttribute,
    onAttributeChangeName,
    onAttributeChangeType,
    onAttributeChangeValue,
    onAttributeRemove,
    resetAttributes,
  } = useAttributesTestResult({ mode: "create", setValue })
  const attributes = filterAttributesByStatus(allAttributes, statuses, watchStatus)

  const [steps, setSteps] = useState<Record<string, number>>({})
  const { onHandleError } = useErrors<ErrorData>(setErrors)

  const onCloseModal = () => {
    setIsShow(false)
    setSteps({})
    setErrors(null)
    onReset()
    removeAttachmentIds()
    resetAttributes()
    reset()
  }

  const handleCancel = () => {
    if (isLoading || isLoadingCreateAttachment) {
      return
    }

    if (isDirty) {
      showModal(onCloseModal)
      return
    }

    onCloseModal()
  }

  const onSubmit: SubmitHandler<ResultFormData> = async (data) => {
    if (!drawerTest) return
    setErrors(null)

    const { isSuccess, attributesJson, errors: attributesErrors } = makeAttributesJson(attributes)

    if (!isSuccess) {
      setErrors({ attributes: JSON.stringify(attributesErrors) })
      return
    }

    const stepsResult: { step: string; status: number }[] = []
    if (testCase.steps.length) {
      testCase.steps.forEach((step) => {
        if (steps[step.id] === undefined || steps[step.id] === null) {
          console.error(`Step ${step.id} is not selected`)
        } else {
          stepsResult.push({ step: step.id, status: steps[step.id] })
        }
      })
    }

    try {
      const dataReq = {
        ...data,
        attributes: attributesJson,
        test: drawerTest.id,
        steps_results: stepsResult,
      } as ResultCreate
      const newResult = await createResult({
        testPlanId: Number(testPlanId),
        body: dataReq,
      }).unwrap()
      onCloseModal()

      notification.success({
        message: t("Success"),
        closable: true,
        description: (
          <AlertSuccessChange
            action="created"
            title={t("Result")}
            link={`/projects/${project.id}/plans/${testPlanId}/?test=${newResult.test}#result-${newResult.id}`}
            id={String(newResult.id)}
          />
        ),
      })
      onSubmitCb?.(newResult)
    } catch (err: unknown) {
      onHandleError(err)
    }
  }

  useEffect(() => {
    if (defaultStatus && !watchStatus && isShow) {
      setValue("status", defaultStatus.id, { shouldDirty: true })
      const newSteps = testCase.steps.reduce(
        (acc, step) => {
          if (step.id) {
            acc[step.id] = defaultStatus.id
          }
          return acc
        },
        {} as Record<string, number>
      )
      setSteps(newSteps)
    }
  }, [defaultStatus, isShow, watchStatus])

  const isAllStepsSelected = testCase.steps.every((step) => steps[step.id])

  return {
    isLoading,
    isLoadingCreateAttachment,
    isDirty,
    attachments,
    attachmentsIds,
    control,
    attributes,
    steps,
    errors,
    onLoad,
    onChange,
    onRemove,
    handleSubmitForm: handleSubmit(onSubmit),
    handleCancel,
    setValue,
    register,
    addAttribute,
    onAttributeChangeName,
    onAttributeChangeType,
    onAttributeChangeValue,
    onAttributeRemove,
    setSteps,
    setAttachments,
    statuses,
    disabled: !isDirty || isLoading || !watchStatus || !isAllStepsSelected,
  }
}
