import { Attachment } from "shared/ui"

import { useTestSuiteContext } from "../test-suite-layout"

export const TestSuitesAttachmentsTab = () => {
  const { suite } = useTestSuiteContext()
  return <Attachment.List attachments={suite?.attachments ?? []} />
}
