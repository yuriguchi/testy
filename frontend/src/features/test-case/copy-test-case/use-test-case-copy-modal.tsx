import { notification } from "antd"
import { useState } from "react"
import { SubmitHandler, useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"
import { useParams } from "react-router-dom"

import { useCopyTestCaseMutation } from "entities/test-case/api"

import { initInternalError } from "shared/libs"
import { AlertSuccessChange } from "shared/ui"

interface FormTestCaseCopy {
  newName: string
  suite: SelectData | null
}

interface Props {
  testCase: TestCase
  onSubmit?: (suite: TestCase) => void
}

export const useTestCaseCopyModal = ({ testCase, onSubmit: cbOnSubmit }: Props) => {
  const { t } = useTranslation()
  const { testSuiteId } = useParams<ParamProjectId & ParamTestSuiteId>()
  const [isShow, setIsShow] = useState(false)
  const [copyTestCase, { isLoading }] = useCopyTestCaseMutation()
  const {
    handleSubmit,
    control,
    formState: { errors: formErrors },
  } = useForm<FormTestCaseCopy>({
    defaultValues: {
      newName: `${testCase.name}(Copy)`,
      suite: null,
    },
  })

  const handleCancel = () => {
    setIsShow(false)
  }

  const handleShow = () => {
    setIsShow(true)
  }

  const onSubmit: SubmitHandler<FormTestCaseCopy> = async (data) => {
    try {
      const dstSuiteId = testSuiteId ?? ""
      const newTestCase = await copyTestCase({
        cases: [{ id: String(testCase.id), new_name: data.newName }],
        dst_suite_id: data.suite ? String(data.suite.value) : dstSuiteId,
      }).unwrap()
      notification.success({
        message: t("Success"),
        closable: true,
        description: (
          <AlertSuccessChange id={String(testCase.id)} action="copied" title={t("Test Case")} />
        ),
      })
      handleCancel()
      cbOnSubmit?.(newTestCase[0])
    } catch (err) {
      initInternalError(err)
    }
  }

  return {
    isShow,
    isLoading,
    control,
    formErrors,
    handleSubmit: handleSubmit(onSubmit),
    handleShow,
    handleCancel,
  }
}
