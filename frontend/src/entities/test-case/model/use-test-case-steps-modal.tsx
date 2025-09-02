import { useContext, useEffect } from "react"
import { SubmitHandler, useForm } from "react-hook-form"

import { useAttachments } from "entities/attachment/model"

import { ProjectContext } from "pages/project"

import { useShowModalCloseConfirm } from "shared/hooks"

interface FormData {
  name: string
  scenario: string
  expected?: string
  attachments?: IAttachment[]
}

export interface TestCaseStepsModalProps {
  isEdit: boolean
  step: Step | null
  onCloseModal: () => void
  onSubmit: (step: Step) => void
}

export const useTestCaseStepsModal = ({
  step,
  onSubmit,
  onCloseModal,
}: TestCaseStepsModalProps) => {
  const { project } = useContext(ProjectContext)!
  const { showModal } = useShowModalCloseConfirm()
  const {
    handleSubmit,
    control,
    setValue,
    register,
    clearErrors,
    formState: { isDirty, errors },
  } = useForm<FormData>({
    defaultValues: {
      name: "",
      scenario: "",
      expected: "",
      attachments: [],
    },
  })

  const { attachments, attachmentsIds, isLoading, setAttachments, onRemove, onLoad, onChange } =
    useAttachments<FormData>(control, project.id)

  const onCloseModalSteps = () => {
    onCloseModal()
    clearErrors()
  }

  const handleClose = () => {
    if (isDirty) {
      showModal(onCloseModalSteps)
      return
    }

    onCloseModalSteps()
  }

  const onSubmitForm: SubmitHandler<FormData> = ({ name, scenario, expected }) => {
    if (!step) return

    onSubmit({
      id: step.id,
      name,
      scenario,
      expected,
      sort_order: step.sort_order,
      attachments,
    })
  }

  useEffect(() => {
    if (!step) return
    const testResultAttachesWithUid = step.attachments.map((attach) => ({
      ...attach,
      uid: String(attach.id),
    }))

    setValue("name", step.name)
    setValue("scenario", step.scenario)
    setValue("expected", step.expected)
    setAttachments(testResultAttachesWithUid)
    clearErrors()
  }, [step])

  return {
    handleClose,
    handleSubmit,
    onSubmitForm,
    isLoading,
    isDirty,
    errors,
    control,
    onLoad,
    attachments,
    setAttachments,
    attachmentsIds,
    setValue,
    onChange,
    register,
    onRemove,
  }
}
