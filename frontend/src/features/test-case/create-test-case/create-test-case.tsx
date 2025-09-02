import { PlusOutlined } from "@ant-design/icons"
import { Button } from "antd"
import { ReactNode } from "react"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate, useParams } from "react-router-dom"
import { v4 as uuidv4 } from "uuid"

import { savePrevPageSearch } from "shared/libs"

interface Props {
  as?: ReactNode
  parentSuiteId?: number
}

export const CreateTestCase = ({ as, parentSuiteId: initParentSuiteId }: Props) => {
  const { t } = useTranslation()
  const { projectId, testSuiteId } = useParams<ParamProjectId | ParamTestSuiteId>()
  const parentSuiteId = initParentSuiteId ?? testSuiteId
  const navigate = useNavigate()
  const location = useLocation()

  const handleClick = () => {
    const searchParams = new URLSearchParams(location.search)
    const uniqId = uuidv4()
    if (searchParams.size) {
      savePrevPageSearch(uniqId, location.search.slice(1))
    }

    let url = `/projects/${projectId}/suites/${parentSuiteId}/new-test-case`
    if (searchParams.size) {
      url += `?prevSearch=${uniqId}`
    }
    navigate(url)
  }

  if (as) {
    return (
      <div id="create-test-case" onClick={handleClick}>
        {as}
      </div>
    )
  }

  return (
    <Button id="create-test-case" type="primary" icon={<PlusOutlined />} onClick={handleClick}>
      {t("Create")} {t("Test Case")}
    </Button>
  )
}
