import { Link } from "react-router-dom"

interface TestPlanActivityLinkProps {
  projectId: string
  planId: string
  title: string
  isVisibleSeparator: boolean
}

export const TestPlanActivityLink = ({
  projectId,
  planId,
  title,
  isVisibleSeparator,
}: TestPlanActivityLinkProps) => {
  return (
    <div data-testid={`test-plan-activity-link-container-${title}`}>
      <Link
        to={`/projects/${projectId}/plans/${planId}`}
        data-testid={`test-plan-activity-link-${title}`}
      >
        {title}
      </Link>
      {isVisibleSeparator && <span className="ant-breadcrumb-separator">/</span>}
    </div>
  )
}
