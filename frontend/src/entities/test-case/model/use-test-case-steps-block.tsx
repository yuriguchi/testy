import { useState } from "react"
import { v4 as uuidv4 } from "uuid"

export interface TestCaseStepsBlockProps {
  steps: Step[]
  setSteps: (steps: Step[]) => void
}

export const useTestCaseStepsBlock = ({ steps, setSteps }: TestCaseStepsBlockProps) => {
  const [modalStep, setModalStep] = useState<Step | null>(null)
  const [isEdit, setIsEdit] = useState(false)
  const [isInitialSteps, setIsInitiallSteps] = useState(true)

  const getLastSortOrder = () => {
    return steps.reduce((acc, shot) => (acc > shot.sort_order ? acc : shot.sort_order), 0)
  }

  const handleStep = (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => {
    event.preventDefault()
    const sortOrder = getLastSortOrder()

    // generate random id to use as unique react key prop
    const newStep = {
      id: uuidv4(),
      name: "",
      scenario: "",
      expected: "",
      sort_order: sortOrder + 1,
      attachments: [],
    }

    setModalStep(newStep)
    setIsEdit(false)
  }

  const handleAddStep = (step: Step) => {
    const newSteps = steps.concat(step)
    setSteps(newSteps)
    setModalStep(null)
  }

  const handleEditStep = (step: Step) => {
    const newSteps = steps.map((item) => {
      if (item.id === step.id) {
        return {
          id: item.id,
          name: step.name,
          scenario: step.scenario,
          expected: step.expected,
          sort_order: item.sort_order,
          attachments: step.attachments,
        }
      }
      return item
    })

    setSteps(newSteps)
    setModalStep(null)
  }

  const handleSubmit = (step: Step) => {
    if (isEdit) {
      handleEditStep(step)
      return
    }

    handleAddStep(step)
  }

  const handleClickEditStep = (step: Step) => {
    setIsEdit(true)
    setModalStep(step)
  }

  const handleClickCloseModal = () => {
    setIsEdit(false)
    setModalStep(null)
  }

  const handleDeleteStep = (stepId: string) => {
    const newSteps = steps.filter((i) => i.id !== stepId)
    setSteps(newSteps)
  }

  const handleSortSteps = (newSteps: Step[]) => {
    if (isInitialSteps) {
      setIsInitiallSteps(false)
      return
    }

    const newStepsList = newSteps.map((step, index) => ({
      ...step,
      sort_order: index + 1,
    }))
    setSteps(newStepsList)
  }

  return {
    handleStep,
    handleSortSteps,
    handleDeleteStep,
    handleClickCloseModal,
    handleClickEditStep,
    isEdit,
    modalStep,
    handleSubmit,
  }
}
