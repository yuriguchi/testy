import { notification } from "antd"
import dayjs from "dayjs"
import { TreebarContext } from "processes"
import { useContext, useEffect, useState } from "react"
import { SubmitHandler, useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate, useSearchParams } from "react-router-dom"

import { useAttachments } from "entities/attachment/model"

import { useGetParametersQuery } from "entities/parameter/api"

import {
  useCreateTestPlanMutation,
  useGetTestPlanCasesQuery,
  useLazyGetTestPlanAncestorsQuery,
  useLazyGetTestPlanQuery,
  useUpdateTestPlanMutation,
} from "entities/test-plan/api"
import { useAttributesTestPlan } from "entities/test-plan/model"

import { ProjectContext } from "pages/project"

import { useDatepicker, useErrors, useShowModalCloseConfirm } from "shared/hooks"
import { makeAttributesJson, makeParametersForTreeView } from "shared/libs"
import { AlertSuccessChange } from "shared/ui"

import { refetchNodeAfterCreateOrCopy, refetchNodeAfterEdit } from "widgets/[ui]/treebar/utils"

type TabType = "general" | "attachments"

export interface ErrorData {
  name?: string
  description?: string
  parent?: string
  test_cases?: string
  started_at?: string
  due_date?: string
  parameters?: string
  attributes?: string
}

interface LocationState {
  testPlan?: TestPlan
}

export type ChangeTestPlanForm = Modify<
  TestPlanCreate,
  {
    started_at: dayjs.Dayjs
    due_date: dayjs.Dayjs
    attributes: Attribute[]
  }
>

interface Props {
  type: "create" | "edit"
}

const formDefaultVales = {
  name: "",
  description: "",
  parent: null,
  test_cases: [],
  parameters: [],
  started_at: dayjs(),
  due_date: dayjs().add(1, "day"),
  attributes: [],
  attachments: [],
}

export const useChangeTestPlan = ({ type }: Props) => {
  const { t } = useTranslation()
  const location = useLocation()
  const [searchParams] = useSearchParams()
  const { project } = useContext(ProjectContext)!
  const { showModal } = useShowModalCloseConfirm()
  const navigate = useNavigate()
  const state = location.state as LocationState | null
  const { treebar } = useContext(TreebarContext)!

  const {
    handleSubmit,
    reset,
    control,
    setValue,
    formState: { isDirty, errors: formErrors },
    register,
  } = useForm<ChangeTestPlanForm>({
    defaultValues: formDefaultVales,
  })

  const { setDateFrom, setDateTo, disabledDateFrom, disabledDateTo } = useDatepicker()
  const {
    attachments,
    attachmentsIds,
    isLoading: isLoadingAttachments,
    setAttachments,
    onLoad: handleAttachmentLoad,
    onRemove: handleAttachmentRemove,
    onChange: handleAttachmentChange,
  } = useAttachments<ChangeTestPlanForm>(control, project.id)

  const {
    attributes,
    isLoading: isLoadingAttributes,
    addAttribute,
    onAttributeChangeName,
    onAttributeChangeType,
    onAttributeChangeValue,
    onAttributeRemove,
    getAttributeJson,
    setAttributes,
  } = useAttributesTestPlan({ mode: type, setValue })

  const [stateTestPlan, setStateTestPlan] = useState<TestPlan | null>(state?.testPlan ?? null)
  const [parametersTreeView, setParametersTreeView] = useState<IParameterTreeView[]>([])

  const [selectedParent, setSelectedParent] = useState<{ label: string; value: number } | null>(
    null
  )
  const [tab, setTab] = useState<TabType>("general")
  const [errors, setErrors] = useState<ErrorData | null>(null)
  const { onHandleError } = useErrors<ErrorData>(setErrors)

  const { data: parameters } = useGetParametersQuery(project.id)
  const [getTestPlan, { isLoading: isLoadingGetTestPlan }] = useLazyGetTestPlanQuery()
  const [getAncestors] = useLazyGetTestPlanAncestorsQuery()
  const [createTestPlan, { isLoading: isLoadingCreateTestPlan }] = useCreateTestPlanMutation()
  const [updateTestPlan, { isLoading: isLoadingUpdateTestPlan }] = useUpdateTestPlanMutation()
  const { data: tests, isLoading: isLoadingTestCases } = useGetTestPlanCasesQuery(
    {
      testPlanId: String(stateTestPlan?.id),
    },
    { skip: type === "create" && !stateTestPlan }
  )

  const refetchParentAfterCreate = async (updatedEntity: TestPlan) => {
    if (!treebar.current) {
      return
    }

    await refetchNodeAfterCreateOrCopy(treebar.current, updatedEntity)
  }

  const refetchParentAfterEdit = async (updatedEntity: TestPlan, oldEntity: TestPlan) => {
    if (!treebar.current) {
      return
    }

    const fetchAncestors = (id: number) => {
      return getAncestors(
        {
          id,
          project: oldEntity.project,
        },
        false
      ).unwrap()
    }

    await refetchNodeAfterEdit(treebar.current, updatedEntity, oldEntity, fetchAncestors)
  }

  const handleTabChange = (activeKey: string) => {
    setTab(activeKey as TabType)
  }

  const clear = () => {
    setErrors(null)
    reset()
  }

  const redirectToPrev = () => {
    clear()
    const prevUrl = searchParams.get("prevUrl")
    navigate(prevUrl ?? `/projects/${project.id}/plans/${stateTestPlan?.id ?? ""}`)
  }

  const handleCancel = () => {
    if (isDirty) {
      showModal(redirectToPrev)
      return
    }

    redirectToPrev()
  }

  const redirectToPlan = (testPlanId?: number) => {
    const prevUrl = searchParams.get("prevUrl")
    if (prevUrl && type === "edit") {
      navigate(prevUrl)
      return
    }

    navigate(`/projects/${project.id}/plans/${testPlanId ?? ""}`)
  }

  const onSubmitEdit: SubmitHandler<ChangeTestPlanForm> = async (data) => {
    if (!stateTestPlan) return

    setErrors(null)
    const newTestCases = data.test_cases?.filter((item) => !item.startsWith("TS"))
    const { isSuccess, attributesJson, errors: attributeErrors } = makeAttributesJson(attributes)

    if (!isSuccess) {
      setErrors({ attributes: JSON.stringify(attributeErrors) })
      return
    }

    try {
      const newPlan = await updateTestPlan({
        id: stateTestPlan.id,
        body: {
          ...data,
          due_date: data.due_date.format("YYYY-MM-DDThh:mm"),
          started_at: data.started_at.format("YYYY-MM-DDThh:mm"),
          parent: data.parent ?? null,
          test_cases: newTestCases,
          attributes: attributesJson,
        },
      }).unwrap()
      notification.success({
        message: t("Success"),
        closable: true,
        description: (
          <AlertSuccessChange
            id={String(newPlan.id)}
            action="updated"
            title={t("Test Plan")}
            link={`/projects/${project.id}/plans/${newPlan.id}`}
          />
        ),
      })
      clear()
      refetchParentAfterEdit(newPlan, stateTestPlan)
      redirectToPlan(stateTestPlan.id)
    } catch (err) {
      onHandleError(err)
    }
  }

  const onSubmitCreate: SubmitHandler<ChangeTestPlanForm> = async (data) => {
    setErrors(null)
    try {
      const newTestCases = data.test_cases?.filter((item) => !item.startsWith("TS"))
      const { isSuccess, attributesJson, errors: attributeErrors } = makeAttributesJson(attributes)
      if (!isSuccess) {
        setErrors({ attributes: JSON.stringify(attributeErrors) })
        return
      }

      const newTestPlan = await createTestPlan({
        ...data,
        test_cases: newTestCases,
        project: project.id,
        attributes: attributesJson,
      }).unwrap()
      notification.success({
        message: t("Success"),
        closable: true,
        description: (
          <AlertSuccessChange
            id={String(newTestPlan[0].id)}
            action="created"
            title={t("Test Plan")}
            link={`/projects/${project.id}/plans/${newTestPlan[0].id}`}
          />
        ),
      })
      clear()
      refetchParentAfterCreate(newTestPlan[0])
      redirectToPlan(newTestPlan[0].id)
    } catch (err: unknown) {
      onHandleError(err)
    }
  }

  const handleSelectTestPlan = (value: SelectData | null) => {
    setErrors({ parent: "" })
    if (type === "edit" && Number(value?.value) === Number(stateTestPlan?.id)) {
      setErrors({ parent: t("Test Plan cannot be its own parent.") })
      return
    }

    setValue("parent", value ? value.value : null, { shouldDirty: true })
    setSelectedParent(value ? { value: value.value, label: value.label?.toString() ?? "" } : null)
  }

  useEffect(() => {
    if (parameters) {
      setParametersTreeView(makeParametersForTreeView(parameters))
    }
  }, [parameters])

  useEffect(() => {
    const parentTestPlanId = searchParams.get("parentTestPlan")
    if (!parentTestPlanId || (parentTestPlanId && stateTestPlan)) {
      return
    }

    const fetchParentPlan = async () => {
      const plan = await getTestPlan({
        project: project.id,
        testPlanId: parentTestPlanId,
      }).unwrap()
      setSelectedParent({ value: plan.id, label: plan.name })
    }

    fetchParentPlan()
  }, [stateTestPlan, searchParams.get("parentTestPlan")])

  useEffect(() => {
    if (!stateTestPlan || isLoadingAttributes) return

    if (type === "create") {
      reset(formDefaultVales)
      setSelectedParent({ value: stateTestPlan.id, label: stateTestPlan.name })
      setValue("parent", stateTestPlan.id, { shouldDirty: false })
    } else if (type === "edit" && tests) {
      const attachesWithUid = stateTestPlan?.attachments?.map((attach) => ({
        ...attach,
        uid: String(attach.id),
      }))
      if (attachesWithUid?.length) {
        setAttachments(attachesWithUid)
      }

      const attrs = getAttributeJson(stateTestPlan.attributes)
      setAttributes(attrs)

      reset({
        name: stateTestPlan.name,
        description: stateTestPlan.description,
        parent: stateTestPlan.parent?.id ?? null,
        test_cases: tests.case_ids.map((i) => String(i)),
        started_at: dayjs(stateTestPlan.started_at),
        due_date: stateTestPlan.due_date ? dayjs(stateTestPlan.due_date) : undefined,
        attributes: attrs,
      })

      setSelectedParent(
        stateTestPlan.parent
          ? { value: stateTestPlan.parent.id, label: stateTestPlan.parent.name }
          : null
      )
    }
  }, [stateTestPlan, tests, type, isLoadingAttributes])

  useEffect(() => {
    setStateTestPlan(state?.testPlan ?? null)
  }, [state?.testPlan])

  return {
    errors,
    formErrors,
    tab,
    isDirty,
    isLoadingSubmit:
      isLoadingCreateTestPlan ||
      isLoadingUpdateTestPlan ||
      isLoadingGetTestPlan ||
      isLoadingAttachments ||
      isLoadingTestCases,
    control,
    selectedParent,
    attachments,
    attachmentsIds,
    parametersTreeView,
    stateTestPlan,
    setDateFrom,
    disabledDateFrom,
    setDateTo,
    disabledDateTo,
    handleSelectTestPlan,
    setAttachments,
    handleAttachmentLoad,
    handleAttachmentRemove,
    handleAttachmentChange,
    setValue,
    handleTabChange,
    handleCancel,
    handleSubmitForm: handleSubmit(type === "create" ? onSubmitCreate : onSubmitEdit),
    register,
    attributes,
    addAttribute,
    onAttributeChangeName,
    onAttributeChangeType,
    onAttributeChangeValue,
    onAttributeRemove,
  }
}
