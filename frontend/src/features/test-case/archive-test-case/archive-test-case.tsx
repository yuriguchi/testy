import { Dropdown, MenuProps } from "antd"
import { useState } from "react"
import { useTranslation } from "react-i18next"

import { DeleteTestCase } from "../delete-test-case/delete-test-case"
import { ArchiveTestCaseModal } from "./archive-test-case-modal"

interface Props {
  testCase: TestCase
  onSubmit?: (testCase: TestCase) => void
}

export const ArchiveTestCase = ({ testCase, onSubmit }: Props) => {
  const { t } = useTranslation()
  const [isShow, setIsShow] = useState(false)

  const items: MenuProps["items"] = [
    {
      key: "1",
      label: <DeleteTestCase testCase={testCase} onSubmit={onSubmit} />,
    },
  ]

  return (
    <>
      <Dropdown.Button
        className="archive-test-case"
        menu={{ items }}
        danger
        style={{ width: "fit-content" }}
        onClick={() => setIsShow(true)}
        data-testid="archive-test-case-btn"
      >
        {t("Archive")}
      </Dropdown.Button>
      <ArchiveTestCaseModal
        isShow={isShow}
        setIsShow={setIsShow}
        testCase={testCase}
        onSubmit={onSubmit}
      />
    </>
  )
}
