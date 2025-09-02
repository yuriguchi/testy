import { notification } from "antd"
import { TreebarContext } from "processes"
import { useContext, useEffect, useState } from "react"
import { SubmitHandler, useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate, useSearchParams } from "react-router-dom"

import { useAttachments } from "entities/attachment/model"

import { useGetParametersQuery } from "entities/parameter/api"

import {
  useCreateSuiteMutation,
  useLazyGetSuiteQuery,
  useLazyGetTestSuiteAncestorsQuery,
  useUpdateTestSuiteMutation,
} from "entities/suite/api"
import { useAttributesTestSuite } from "entities/suite/model"

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
  attributes?: string
}

interface LocationState {
  suite?: Suite
}

export type ChangeTestSuiteForm = Modify<
  SuiteUpdate,
  {
    attributes: Attribute[]
  }
>

interface Props {
  type: "create" | "edit"
}

const formDefaultValues = {
  name: "",
  description: "",
  parent: null,
  attributes: [],
  attachments: [],
}

export const useChangeTestSuite = ({ type }: Props) => {
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
  } = useForm<ChangeTestSuiteForm>({
    defaultValues: formDefaultValues,
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
  } = useAttachments<ChangeTestSuiteForm>(control, project.id)

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
  } = useAttributesTestSuite({ mode: type, setValue })

  const [stateTestSuite, setStateTestSuite] = useState<Suite | null>(state?.suite ?? null)
  const [parametersTreeView, setParametersTreeView] = useState<IParameterTreeView[]>([])

  const [selectedParent, setSelectedParent] = useState<{ label: string; value: number } | null>(
    null
  )
  const [tab, setTab] = useState<TabType>("general")
  const [errors, setErrors] = useState<ErrorData | null>(null)
  const { onHandleError } = useErrors<ErrorData>(setErrors)

  const { data: parameters } = useGetParametersQuery(project.id)
  const [getTestSuite, { isLoading: isLoadingGetTestSuite }] = useLazyGetSuiteQuery()
  const [getAncestors] = useLazyGetTestSuiteAncestorsQuery()
  const [createTestSuite, { isLoading: isLoadingCreateTestSuite }] = useCreateSuiteMutation()
  const [updateTestSuite, { isLoading: isLoadingUpdateTestSuite }] = useUpdateTestSuiteMutation()

  const refetchParentAfterCreate = async (updatedEntity: Suite) => {
    if (!treebar.current) {
      return
    }

    await refetchNodeAfterCreateOrCopy(treebar.current, updatedEntity)
  }

  const refetchParentAfterEdit = async (updatedEntity: SuiteResponseUpdate, oldEntity: Suite) => {
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
    navigate(prevUrl ?? `/projects/${project.id}/suites/${stateTestSuite?.id ?? ""}`)
  }

  const handleCancel = () => {
    if (isDirty) {
      showModal(redirectToPrev)
      return
    }

    redirectToPrev()
  }

  const redirectToSuite = (suiteId?: number) => {
    const prevUrl = searchParams.get("prevUrl")
    if (prevUrl && type === "edit") {
      navigate(prevUrl)
      return
    }

    navigate(`/projects/${project.id}/suites/${suiteId ?? ""}`)
  }

  const onSubmitEdit: SubmitHandler<ChangeTestSuiteForm> = async (data) => {
    if (!stateTestSuite) return
    setErrors(null)
    try {
      const { isSuccess, attributesJson, errors: attributeErrors } = makeAttributesJson(attributes)
      if (!isSuccess) {
        setErrors({ attributes: JSON.stringify(attributeErrors) })
        return
      }

      const newSuite = await updateTestSuite({
        id: stateTestSuite.id,
        body: {
          ...data,
          parent: data.parent ? Number(data.parent) : null,
          attributes: attributesJson,
        },
      }).unwrap()
      notification.success({
        message: t("Success"),
        closable: true,
        description: (
          <AlertSuccessChange
            id={String(stateTestSuite.id)}
            action="updated"
            title={t("Test Suite")}
            link={`/projects/${project.id}/suites/${stateTestSuite.id}`}
          />
        ),
      })
      clear()
      refetchParentAfterEdit(newSuite, stateTestSuite)
      redirectToSuite(stateTestSuite.id)
    } catch (err) {
      onHandleError(err)
    }
  }

  const onSubmitCreate: SubmitHandler<ChangeTestSuiteForm> = async (data) => {
    setErrors(null)
    try {
      const { isSuccess, attributesJson, errors: attributeErrors } = makeAttributesJson(attributes)
      if (!isSuccess) {
        setErrors({ attributes: JSON.stringify(attributeErrors) })
        return
      }

      const newSuite = await createTestSuite({
        ...data,
        project: project.id,
        attributes: attributesJson,
      }).unwrap()

      notification.success({
        message: t("Success"),
        closable: true,
        description: (
          <AlertSuccessChange
            action="created"
            title={t("Test Suite")}
            link={`/projects/${project.id}/suites/${newSuite.id}`}
            id={String(newSuite.id)}
          />
        ),
      })
      clear()
      refetchParentAfterCreate(newSuite)
      redirectToSuite(newSuite.id)
    } catch (err: unknown) {
      onHandleError(err)
    }
  }

  const handleSelectTestSuite = (value: SelectData | null) => {
    setErrors({ parent: "" })
    if (type === "edit" && Number(value?.value) === Number(stateTestSuite?.id)) {
      setErrors({ parent: t("Test Suite cannot be its own parent.") })
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
    const parentTestSuiteId = searchParams.get("parentTestSuite")
    if (!parentTestSuiteId || (parentTestSuiteId && stateTestSuite)) {
      return
    }

    const fetchParentSuite = async () => {
      const suite = await getTestSuite({
        suiteId: parentTestSuiteId,
      }).unwrap()
      setSelectedParent({ value: suite.id, label: suite.name })
    }

    fetchParentSuite()
  }, [stateTestSuite, searchParams.get("parentTestSuite")])

  useEffect(() => {
    if (!stateTestSuite || isLoadingAttributes) return

    if (type === "create") {
      reset(formDefaultValues)
      setSelectedParent({ value: stateTestSuite.id, label: stateTestSuite.name })
      setValue("parent", stateTestSuite.id, { shouldDirty: false })
    } else if (type === "edit") {
      const attachesWithUid = stateTestSuite?.attachments?.map((attach) => ({
        ...attach,
        uid: String(attach.id),
      }))
      if (attachesWithUid?.length) {
        setAttachments(attachesWithUid)
      }

      const attrs = getAttributeJson(stateTestSuite.attributes)
      setAttributes(attrs)

      reset({
        name: stateTestSuite.name,
        description: stateTestSuite.description,
        parent: stateTestSuite.parent?.id ?? null,
        attributes: attrs,
      })

      setSelectedParent(
        stateTestSuite.parent
          ? { value: stateTestSuite.parent.id, label: stateTestSuite.parent.name }
          : null
      )
    }
  }, [stateTestSuite, type, isLoadingAttributes])

  useEffect(() => {
    setStateTestSuite(state?.suite ?? null)
  }, [state?.suite])

  return {
    errors,
    formErrors,
    tab,
    isDirty,
    isLoadingSubmit:
      isLoadingCreateTestSuite ||
      isLoadingUpdateTestSuite ||
      isLoadingGetTestSuite ||
      isLoadingAttachments,
    control,
    selectedParent,
    attachments,
    attachmentsIds,
    parametersTreeView,
    stateTestSuite,
    setDateFrom,
    disabledDateFrom,
    setDateTo,
    disabledDateTo,
    handleSelectTestSuite,
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
