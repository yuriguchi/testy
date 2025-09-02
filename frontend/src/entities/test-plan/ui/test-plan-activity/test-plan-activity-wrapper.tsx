import { Typography } from "antd"
import { useTranslation } from "react-i18next"
import { useParams } from "react-router"
import { Link } from "react-router-dom"

import { ContainerLoader } from "shared/ui"

import { useGetTestPlanQuery } from "../../api"
import { useTestPlanActivity } from "../../model"
import { TestPlanActivityFilers } from "./test-plan-activity-filters"
import { TestPlanActivityTable } from "./test-plan-activity-table"

export const TestPlanActivityWrapper = () => {
  const { t } = useTranslation()
  const testPlanActivity = useTestPlanActivity()
  const { testPlanId, projectId } = useParams<ParamTestPlanId & ParamProjectId>()
  const { data: testPlan, isLoading } = useGetTestPlanQuery(
    { testPlanId: String(testPlanId), project: Number(projectId) },
    {
      skip: !testPlanId || !projectId,
    }
  )

  if (isLoading || !testPlan || !projectId || !testPlanId) return <ContainerLoader />

  return (
    <div>
      <Typography.Text
        style={{ fontSize: 20, marginBottom: 24, display: "block" }}
        data-testid="test-plan-activity-title"
      >
        {t("Activity")} -{" "}
        <Link
          to={`/projects/${projectId}/plans/${testPlanId}`}
          data-testid="test-plan-activity-title-link"
        >
          {testPlan.title}
        </Link>
      </Typography.Text>
      <TestPlanActivityFilers testPlanActivity={testPlanActivity} />
      <TestPlanActivityTable testPlanActivity={testPlanActivity} />
    </div>
  )
}
