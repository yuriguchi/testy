import { EditOutlined } from "@ant-design/icons"
import { Button } from "antd"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate, useParams } from "react-router-dom"
import { v4 as uuidv4 } from "uuid"

import { useAppDispatch } from "app/hooks"

import { clearDrawerTestCase } from "entities/test-case/model"

import { savePrevPageSearch } from "shared/libs"

interface Props {
  testCase: TestCase
}

export const EditTestCase = ({ testCase }: Props) => {
  const { t } = useTranslation()
  const { projectId, testSuiteId } = useParams<ParamProjectId | ParamTestSuiteId>()
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const location = useLocation()

  const handleEdit = () => {
    dispatch(clearDrawerTestCase())
    const searchParams = new URLSearchParams(location.search)
    searchParams.delete("test_case")

    const uniqId = uuidv4()
    if (searchParams.size) {
      savePrevPageSearch(uniqId, searchParams.toString())
    }

    navigate(
      `/projects/${projectId}/suites/${testSuiteId}/edit-test-case?test_case=${testCase.id}${
        searchParams.size ? `&prevSearch=${uniqId}` : ""
      }`
    )
  }

  return (
    <Button id="edit-test-case-detail" icon={<EditOutlined />} onClick={handleEdit}>
      {t("Edit")}
    </Button>
  )
}
