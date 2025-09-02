import { Button } from "antd"
import { ReactNode, memo, useState } from "react"
import { useTranslation } from "react-i18next"

import { icons } from "shared/assets/inner-icons"

import { ArchiveTestPlanModal } from "./archive-test-plan-modal"

const { ArchiveIcon } = icons

interface Props {
  as?: ReactNode
  testPlan: TestPlan
  onSubmit?: (plan: TestPlan) => void
}

export const ArchiveTestPlan = memo(({ as, testPlan, onSubmit }: Props) => {
  const { t } = useTranslation()
  const [isShow, setIsShow] = useState(false)

  const handleShow = () => {
    setIsShow(true)
  }

  return (
    <>
      {as ? (
        <div id="archive-test-plan" onClick={handleShow}>
          {as}
        </div>
      ) : (
        <Button
          id="archive-test-plan"
          icon={<ArchiveIcon width={16} height={16} />}
          onClick={handleShow}
        >
          {t("Archive")}
        </Button>
      )}

      <ArchiveTestPlanModal
        isShow={isShow}
        setIsShow={setIsShow}
        testPlan={testPlan}
        onSubmit={onSubmit}
      />
    </>
  )
})

ArchiveTestPlan.displayName = "ArchiveTestPlan"
