import { Attachment } from "shared/ui"

import { useTestPlanContext } from "../test-plan-layout/test-plan-layout"

export const TestPlansAttachmentsTab = () => {
  const { testPlan } = useTestPlanContext()
  return <Attachment.List attachments={testPlan?.attachments ?? []} />
}
