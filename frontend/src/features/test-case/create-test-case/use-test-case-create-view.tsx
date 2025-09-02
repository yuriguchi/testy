import { notification } from "antd"
import { useContext, useEffect, useState } from "react"
import { SubmitHandler, useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"
import { useNavigate, useParams, useSearchParams } from "react-router-dom"

import { useAttachments } from "entities/attachment/model"

import { useTestCaseFormLabels } from "entities/label/model"

import { useCreateTestCaseMutation } from "entities/test-case/api"
import { useAttributesTestCase } from "entities/test-case/model"

import { ProjectContext } from "pages/project"

import { useConfirmBeforeRedirect, useErrors, useShowModalCloseConfirm } from "shared/hooks"
import { getPrevPageSearch, makeAttributesJson } from "shared/libs"
import { AlertSuccessChange } from "shared/ui"

interface SubmitData extends Omit<TestCaseFormData, "steps"> {
  steps?: StepAttachNumber[]
  is_steps: boolean
}

interface ErrorData {
  suite?: string
  name?: string
  setup?: string
  scenario?: string
  expected?: string
  teardown?: string
  estimate?: string
  description?: string
  labels?: string
  attributes?: string | null
}

type TabType = "general" | "attachments"

const getDefaultValues = (projectId: number) => ({
  name: "",
  scenario: "",
  project: projectId,
  suite: undefined,
  expected: "",
  setup: "",
  teardown: "",
  estimate: null,
  description: "",
  attachments: [],
  steps: [],
  is_steps: false,
  labels: [],
  attributes: [],
})

export const useTestCaseCreateView = () => {
  const { t } = useTranslation()
  const { project } = useContext(ProjectContext)!
  const { showModal } = useShowModalCloseConfirm()
  const { testSuiteId } = useParams<ParamTestSuiteId>()
  const [tab, setTab] = useState<TabType>("general")
  const [searchParams] = useSearchParams()

  const navigate = useNavigate()

  const [errors, setErrors] = useState<ErrorData | null>(null)
  const {
    handleSubmit,
    reset,
    control,
    setValue,
    register,
    setError: setFormError,
    formState: { isDirty, errors: formErrors },
    watch,
  } = useForm<TestCaseFormData>({
    defaultValues: getDefaultValues(project.id),
  })

  const isSteps = watch("is_steps")
  const steps = watch("steps")

  const [createTestCase, { isLoading }] = useCreateTestCaseMutation()
  const { onHandleError } = useErrors<ErrorData>(setErrors)
  const {
    attachments,
    attachmentsIds,
    isLoading: isLoadingAttachments,
    setAttachments,
    onRemove,
    onLoad,
    onChange,
    onReset,
  } = useAttachments<TestCaseFormData>(control, project.id)
  const labelProps = useTestCaseFormLabels({
    setValue,
    testCase: null,
    isShow: true,
    isEditMode: false,
  })

  const {
    attributes,
    initAttributes,
    resetAttributes,
    addAttribute,
    onAttributeChangeName,
    onAttributeChangeType,
    onAttributeChangeValue,
    onAttributeRemove,
  } = useAttributesTestCase({ mode: "create", setValue })

  const { setIsRedirectByUser } = useConfirmBeforeRedirect({
    isDirty,
    pathname: "new-test-case",
  })

  const redirectToTestCase = (id?: number) => {
    const prevSearchKey = searchParams.get("prevSearch")
    let url = `/projects/${project.id}/suites/${testSuiteId}`
    if (id !== undefined) {
      url += `?test_case=${id}`
    }
    if (!prevSearchKey) {
      navigate(url)
      return
    }

    const prevSearchResult = getPrevPageSearch(prevSearchKey)
    if (id !== undefined) {
      url += `&${prevSearchResult}`
    } else {
      url += `?${prevSearchResult}`
    }
    navigate(url)
  }

  const handleClose = (id?: number) => {
    setIsRedirectByUser()
    redirectToTestCase(id)
    setErrors(null)
    setTab("general")
    reset()
    onReset()
    resetAttributes()
    labelProps.setLabels([])
    labelProps.setSearchValue("")
  }

  const handleTabChange = (activeKey: string) => {
    setTab(activeKey as TabType)
  }

  const formattingAttachmentForSteps = ({
    id,
    name,
    scenario,
    expected,
    sort_order,
    attachments: attachmentsArgs,
  }: StepAttachNumber) => ({
    id: typeof id === "string" ? undefined : id,
    name,
    scenario,
    expected,
    sort_order,
    attachments: attachmentsArgs.map((x: number | IAttachment) => {
      if (typeof x === "object") return x.id
      return x
    }),
  })

  const onSubmit: SubmitHandler<TestCaseFormData> = async (data) => {
    const dataForm = data as SubmitData

    const { isSuccess, attributesJson, errors: attributesErrors } = makeAttributesJson(attributes)
    if (!isSuccess) {
      setErrors({ attributes: JSON.stringify(attributesErrors) })
      return
    }

    if (data.is_steps && !data.steps?.length) {
      setFormError("steps", { type: "required", message: t("Required field") })
      return
    }

    if (!data.is_steps && !data.scenario?.length) {
      setFormError("scenario", { type: "required", message: t("Required field") })
      return
    }

    setErrors(null)

    try {
      const stepsFormat = dataForm.steps
        ? dataForm.steps.map((step) => formattingAttachmentForSteps(step))
        : []

      const newTestCase = await createTestCase({
        ...dataForm,
        project: project.id,
        is_steps: !!dataForm.is_steps,
        scenario: dataForm.is_steps ? undefined : dataForm.scenario,
        steps: dataForm.is_steps ? stepsFormat : undefined,
        estimate: dataForm.estimate?.length ? dataForm.estimate : undefined,
        suite: Number(testSuiteId),
        attributes: attributesJson,
      }).unwrap()
      handleClose(newTestCase.id)
      notification.success({
        message: t("Success"),
        closable: true,
        description: (
          <AlertSuccessChange
            id={String(newTestCase.id)}
            action="created"
            title={t("Test Case")}
            link={`/projects/${project.id}/suites/${testSuiteId}?test_case=${newTestCase.id}`}
          />
        ),
      })
    } catch (err: unknown) {
      onHandleError(err)
    }
  }

  const handleCancel = () => {
    if (isLoading) return

    if (isDirty) {
      showModal(handleClose)
      return
    }

    handleClose()
  }

  useEffect(() => {
    if (initAttributes.length) {
      reset({ ...getDefaultValues(project.id), attributes: initAttributes })
    }
  }, [initAttributes])

  return {
    isLoading: isLoading || isLoadingAttachments,
    errors,
    formErrors,
    control,
    attachments,
    attachmentsIds,
    steps: steps ?? [],
    isSteps,
    isDirty,
    tab,
    attributes,
    onLoad,
    onRemove,
    onChange,
    setValue,
    setAttachments,
    handleCancel,
    handleSubmitForm: handleSubmit(onSubmit),
    register,
    labelProps,
    handleTabChange,
    addAttribute,
    onAttributeChangeName,
    onAttributeChangeType,
    onAttributeChangeValue,
    onAttributeRemove,
  }
}
