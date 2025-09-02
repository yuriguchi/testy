import { notification } from "antd"
import {
  useCreateCustomAttributeMutation,
  useGetCustomAttributeContentTypesQuery,
  useUpdateCustomAttributeMutation,
} from "entities/custom-attribute/api"
import { useStatuses } from "entities/status/model/use-statuses"
import { useContext, useEffect, useState } from "react"
import { SubmitHandler, useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"

import { ProjectContext } from "pages/project"

import { useErrors, useModal } from "shared/hooks"

interface ErrorData {
  name?: string
  type?: string
  applied_to?: string
}

interface PropsCreate {
  formType: "create"
  attribute?: undefined
}

interface PropsEdit {
  formType: "edit"
  attribute: CustomAttribute
}

export type PropsChangeCustomAttribute = PropsCreate | PropsEdit

const defaultFormValue = {
  is_active: false,
  is_required: false,
}

export const useChangeCustomAttribute = ({ formType, attribute }: PropsChangeCustomAttribute) => {
  const { t } = useTranslation()
  const { project } = useContext(ProjectContext)!
  const { statuses } = useStatuses({ project: project.id })
  const { handleClose: handleCloseModal, handleShow, isShow } = useModal()

  const [createAttribute, { isLoading: isLoadingCreate }] = useCreateCustomAttributeMutation()
  const [updateAttribute, { isLoading: isLoadingUpdate }] = useUpdateCustomAttributeMutation()
  const isLoading = isLoadingCreate || isLoadingUpdate

  const { data: contentTypes } = useGetCustomAttributeContentTypesQuery()

  const [errors, setErrors] = useState<ErrorData | null>(null)
  const { onHandleError } = useErrors<ErrorData>(setErrors)
  const {
    handleSubmit,
    reset,
    control,
    formState: { isDirty },
  } = useForm<CustomAttributeUpdate>({
    defaultValues: {
      name: attribute?.name ?? "",
      type: attribute?.type ?? 0,
      applied_to: {
        testresult: {
          ...defaultFormValue,
          is_suite_specific: false,
          suite_ids: [],
          status_specific: statuses.map((i) => i.id),
        },
        testcase: {
          ...defaultFormValue,
          is_suite_specific: false,
          suite_ids: [],
        },
        testplan: defaultFormValue,
        testsuite: defaultFormValue,
      },
    },
  })

  const onSubmitCreate: SubmitHandler<CustomAttributeUpdate> = async (data) => {
    setErrors(null)

    const countActiveApplied = Object.entries(data.applied_to).reduce(
      (acc, [, value]) => ((value as CustomAttributeAppliedItemBase).is_active ? acc + 1 : acc),
      0
    )

    if (!countActiveApplied) {
      setErrors({ applied_to: t("At least one applied to must be active") })
      return
    }

    const filteredApplied = Object.fromEntries(
      // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
      Object.entries(data.applied_to).filter(([, value]) => value.is_active)
    ) as CustomAttributeAppliedToUpdate

    try {
      await createAttribute({ ...data, project: project.id, applied_to: filteredApplied }).unwrap()
      notification.success({
        message: t("Success"),
        closable: true,
        description: t("Attribute created successfully"),
      })
      handleClose()
    } catch (err) {
      onHandleError(err)
    }
  }

  const onSubmitEdit: SubmitHandler<CustomAttributeUpdate> = async (data) => {
    if (!attribute) return
    setErrors(null)

    const countActiveApplied = Object.entries(data.applied_to).reduce(
      (acc, [, value]) => ((value as CustomAttributeAppliedItemBase).is_active ? acc + 1 : acc),
      0
    )

    if (!countActiveApplied) {
      setErrors({ applied_to: t("At least one applied to must be active") })
      return
    }

    const filteredApplied = Object.fromEntries(
      // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
      Object.entries(data.applied_to).filter(([, value]) => value.is_active)
    ) as CustomAttributeAppliedToUpdate

    try {
      await updateAttribute({
        id: Number(attribute.id),
        body: {
          ...data,
          applied_to: filteredApplied,
        },
      }).unwrap()

      notification.success({
        message: t("Success"),
        closable: true,
        description: t("Attribute edited successfully"),
      })
      handleClose()
    } catch (err) {
      onHandleError(err)
    }
  }

  const handleClose = () => {
    setErrors(null)
    reset()
    handleCloseModal()
  }

  useEffect(() => {
    if (!attribute) return

    reset({
      name: attribute.name,
      type: attribute.type,
      applied_to: {
        testresult: attribute.applied_to.testresult
          ? {
              is_active: true,
              is_required: attribute.applied_to.testresult.is_required,
              is_suite_specific: !!attribute.applied_to.testresult.suite_ids.length,
              suite_ids: attribute.applied_to.testresult.suite_ids,
              status_specific: attribute.applied_to.testresult.status_specific,
            }
          : {
              ...defaultFormValue,
              is_suite_specific: false,
              suite_ids: [],
              status_specific: statuses.map((i) => i.id),
            },
        testcase: attribute.applied_to.testcase
          ? {
              is_active: true,
              is_required: attribute.applied_to.testcase.is_required,
              is_suite_specific: !!attribute.applied_to.testcase.suite_ids.length,
              suite_ids: attribute.applied_to.testcase.suite_ids,
            }
          : {
              ...defaultFormValue,
              is_suite_specific: false,
              suite_ids: [],
            },
        testplan: attribute.applied_to.testplan
          ? {
              is_active: true,
              is_required: attribute.applied_to.testplan.is_required,
            }
          : defaultFormValue,
        testsuite: attribute.applied_to.testsuite
          ? {
              is_active: true,
              is_required: attribute.applied_to.testsuite.is_required,
            }
          : defaultFormValue,
      },
    })
  }, [attribute])

  return {
    isShow,
    control,
    errors,
    isLoading,
    isDirty,
    contentTypes: contentTypes ?? [],
    handleClose,
    handleShow,
    handleSubmitForm: handleSubmit(formType === "create" ? onSubmitCreate : onSubmitEdit),
  }
}
