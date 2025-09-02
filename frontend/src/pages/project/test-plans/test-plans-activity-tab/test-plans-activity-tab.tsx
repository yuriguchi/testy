import { useParams } from "react-router-dom"

import { useTestPlanActivity } from "entities/test-plan/model"
import { TestPlanActivityFilers, TestPlanActivityTable } from "entities/test-plan/ui"

import { ContainerLoader } from "shared/ui"

import { useTestPlanContext } from "../test-plan-layout/test-plan-layout"

export const TestPlanActivityTab = () => {
  const testPlanActivity = useTestPlanActivity()
  const { testPlanId, projectId } = useParams<ParamTestPlanId & ParamProjectId>()
  const { testPlan, isFetching } = useTestPlanContext()

  if (isFetching || !testPlan || !projectId || !testPlanId) return <ContainerLoader />

  return (
    <>
      <TestPlanActivityFilers testPlanActivity={testPlanActivity} />
      <TestPlanActivityTable testPlanActivity={testPlanActivity} />
    </>
  )
}
