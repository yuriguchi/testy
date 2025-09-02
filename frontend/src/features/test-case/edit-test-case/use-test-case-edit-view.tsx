import { Modal, notification } from "antd"
import { useContext, useEffect, useState } from "react"
import { SubmitHandler, useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"
import { useNavigate, useParams, useSearchParams } from "react-router-dom"

import { useAttachments } from "entities/attachment/model"

import { useTestCaseFormLabels } from "entities/label/model"

import { useGetTestSuitesQuery } from "entities/suite/api"

import { useGetTestCaseByIdQuery, useUpdateTestCaseMutation } from "entities/test-case/api"
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
  steps?: string
  expected?: string
  teardown?: string
  estimate?: string
  description?: string
  labels?: string
  attributes?: string | null
}

interface SortingStep {
  id: undefined
  name: string
  scenario: string
  expected: string
  sort_order: number
  attachments: number[]
}

type TabType = "general" | "attachments"

const sortingSteps = (steps: SortingStep[]) => {
  const sortList = steps.sort((a: SortingStep, b: SortingStep) => a.sort_order - b.sort_order)

  return sortList.map((step, index) => ({
    ...step,
    sort_order: index + 1,
  }))
}

export const useTestCaseEditView = () => {
  const { t } = useTranslation()
  const { project } = useContext(ProjectContext)!
  const { showModal } = useShowModalCloseConfirm()
  const navigate = useNavigate()
  const { testSuiteId } = useParams<ParamTestSuiteId>()
  const [searchParams, setSearchParams] = useSearchParams()
  const testCaseId = searchParams.get("test_case")

  const [tab, setTab] = useState<TabType>("general")

  const { data: testCase, isLoading: isLoadingTestCase } = useGetTestCaseByIdQuery(
    { testCaseId: String(testCaseId) },
    {
      skip: !testCaseId,
    }
  )

  const [errors, setErrors] = useState<ErrorData | null>(null)
  const {
    handleSubmit,
    reset,
    control,
    setValue,
    register,
    setError: setFormError,
    clearErrors,
    formState: { isDirty, errors: formErrors },
    watch,
  } = useForm<TestCaseFormData>({
    defaultValues: {
      name: "",
      description: "",
      setup: "",
      scenario: "",
      expected: "",
      teardown: "",
      estimate: null,
      is_steps: false,
      labels: [],
      suite: undefined,
      attributes: [],
      attachments: [],
      steps: [],
    },
  })

  const isSteps = watch("is_steps")
  const steps = watch("steps")

  const [selectedSuite, setSelectedSuite] = useState<SelectData | null>(null)
  const [updateTestCase, { isLoading }] = useUpdateTestCaseMutation()
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

  const {
    attributes,
    isLoading: isLoadingAttributesTestCase,
    setAttributes,
    addAttribute,
    onAttributeChangeName,
    onAttributeChangeType,
    onAttributeChangeValue,
    onAttributeRemove,
    getAttributeJson,
  } = useAttributesTestCase({ mode: "edit", setValue })

  const labelProps = useTestCaseFormLabels({
    setValue,
    testCase: testCase ?? null,
    isShow: true,
    isEditMode: true,
    defaultLabels: testCase?.labels.map((l) => Number(l.id)) ?? [],
  })

  const { data: suites, isLoading: isLoadingSuites } = useGetTestSuitesQuery({
    project: project.id,
  })

  useEffect(() => {
    if (testCase?.suite) {
      setSelectedSuite({ label: testCase.suite.name, value: testCase.suite.id })
      return
    }
  }, [testCase])

  const { setIsRedirectByUser } = useConfirmBeforeRedirect({
    isDirty,
    pathname: "edit-test-case",
  })

  const handleCloseModal = () => {
    setIsRedirectByUser()
    redirectToTestCase()
    setErrors(null)
    setTab("general")
    reset()
    onReset()
    setAttributes([])
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

  const confirmSwitchSuite = () => {
    return new Promise((resolve) => {
      Modal.confirm({
        title: t("Do you want to change suite?"),
        content: t("Please confirm to change suite."),
        okText: t("Ok"),
        cancelText: t("Cancel"),
        onOk: () => resolve(true),
        onCancel: () => resolve(false),
        okButtonProps: { "data-testid": "change-suite-button-confirm" },
        cancelButtonProps: { "data-testid": "change-suite-button-cancel" },
      })
    })
  }

  const onSubmit = async (data: TestCaseFormData, asCurrent = true) => {
    if (!testCase) return
    const dataForm = data as SubmitData

    if (data.is_steps && !data.steps?.length) {
      setFormError("steps", { type: "required", message: t("Required field") })
      return
    }

    if (!data.is_steps && !data.scenario?.length) {
      setFormError("scenario", { type: "required", message: t("Required field") })
      return
    }

    const { isSuccess, attributesJson, errors: attributesErrors } = makeAttributesJson(attributes)
    if (!isSuccess) {
      setErrors({ attributes: JSON.stringify(attributesErrors) })
      return
    }

    const isSwitchingSuite = dataForm.suite && dataForm.suite !== Number(testSuiteId)
    if (isSwitchingSuite) {
      const isConfirmed = await confirmSwitchSuite()
      if (!isConfirmed) return
    }
    setErrors(null)

    try {
      const stepsFormat = dataForm.steps
        ? dataForm.steps.map((step) => formattingAttachmentForSteps(step))
        : []

      const sortSteps = sortingSteps(stepsFormat)

      const newTestCase = await updateTestCase({
        ...testCase,
        ...dataForm,
        attachments: dataForm.attachments,
        is_steps: !!dataForm.is_steps,
        scenario: dataForm.is_steps ? undefined : dataForm.scenario,
        steps: dataForm.is_steps ? sortSteps : [],
        estimate: dataForm.estimate?.length ? dataForm.estimate : null,
        skip_history: asCurrent,
        attributes: attributesJson,
      }).unwrap()
      setSearchParams({
        version: String(newTestCase.versions[0]),
        test_case: String(testCase.id),
      })
      handleCloseModal()
      notification.success({
        message: t("Success"),
        closable: true,
        description: (
          <AlertSuccessChange
            id={String(newTestCase.id)}
            action="updated"
            title={t("Test Case")}
            link={`/projects/${project.id}/suites/${testSuiteId}?test_case=${newTestCase.id}`}
          />
        ),
      })
      if (dataForm.suite !== Number(testSuiteId)) {
        navigate(`/projects/${project.id}/suites/${dataForm.suite}?test_case=${newTestCase.id}`)
      }
    } catch (err: unknown) {
      onHandleError(err)
    }
  }

  const onSubmitWithoutNewVersion: SubmitHandler<TestCaseFormData> = (data) => {
    onSubmit(data, true)
  }

  const onSubmitAsNewVersion: SubmitHandler<TestCaseFormData> = (data) => {
    onSubmit(data, false)
  }

  const handleCancel = () => {
    if (isLoading) return

    if (isDirty) {
      showModal(handleCloseModal)
      return
    }

    handleCloseModal()
  }

  const redirectToTestCase = () => {
    const prevSearchKey = searchParams.get("prevSearch")
    const url = `/projects/${project.id}/suites/${testSuiteId}?test_case=${testCase?.id ?? ""}`

    if (!prevSearchKey) {
      navigate(url)
      return
    }

    const prevSearchResult = getPrevPageSearch(prevSearchKey)
    navigate(`${url}&${prevSearchResult}`)
  }

  const handleSelectSuite = (selectedData: SelectData) => {
    setValue("suite", selectedData.value, { shouldDirty: true })
    setSelectedSuite(selectedData)
  }

  useEffect(() => {
    if (!testCase || isLoadingAttributesTestCase) return

    const testCaseAttachesWithUid = testCase.attachments.map((attach) => ({
      ...attach,
      uid: String(attach.id),
    }))
    const stepsSorted = [...testCase.steps].sort((a, b) => a.sort_order - b.sort_order)
    if (testCaseAttachesWithUid.length) {
      setAttachments(testCaseAttachesWithUid)
    }

    const attrs = getAttributeJson(testCase.attributes)
    setAttributes(attrs)

    reset(
      {
        name: testCase.name,
        description: testCase.description,
        setup: testCase.setup,
        scenario: testCase.scenario ?? "",
        expected: testCase.expected ?? "",
        teardown: testCase.teardown,
        estimate: testCase.estimate,
        steps: stepsSorted,
        is_steps: testCase.is_steps,
        labels: testCase.labels,
        suite: Number(testCase.suite.id),
        attributes: attrs,
        attachments: testCaseAttachesWithUid.map((attach) => attach.id),
      },
      {
        keepDirty: false,
      }
    )
  }, [testCase, isLoadingAttributesTestCase])

  const shouldShowSuiteSelect = !isLoadingSuites
  const title = `${t("Edit Test Case")} '${testCase?.name}'`

  return {
    title,
    isLoading:
      isLoading ||
      isLoadingTestCase ||
      isLoadingAttachments ||
      isLoadingAttributesTestCase ||
      isLoadingSuites,
    errors,
    formErrors,
    control,
    attachments,
    attachmentsIds,
    isSteps,
    isDirty,
    tab,
    selectedSuite,
    shouldShowSuiteSelect,
    suites,
    steps: steps ?? [],
    onLoad,
    onRemove,
    onChange,
    setValue,
    clearErrors,
    setAttachments,
    handleCancel,
    handleSubmitFormAsNew: handleSubmit(onSubmitAsNewVersion),
    handleSubmitFormAsCurrent: handleSubmit(onSubmitWithoutNewVersion),
    register,
    labelProps,
    handleTabChange,
    attributes,
    setAttributes,
    addAttribute,
    onAttributeChangeType,
    onAttributeChangeValue,
    onAttributeChangeName,
    onAttributeRemove,
    handleSelectSuite,
  }
}
