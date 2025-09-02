import { Space, Tag, Typography } from "antd"
import classNames from "classnames"
import dayjs from "dayjs"
import { useContext, useEffect } from "react"
import { useTranslation } from "react-i18next"
import { Link, useLocation, useParams } from "react-router-dom"
import { HashLink } from "react-router-hash-link"

import { useAppSelector } from "app/hooks"

import { useLazyGetResultsQuery } from "entities/result/api"

import { selectDrawerTest } from "entities/test/model"

import { selectArchivedResultsIsShow } from "entities/test-plan/model"

import { UserAvatar } from "entities/user/ui/user-avatar/user-avatar"

import { EditCloneResult } from "features/test-result"

import { colors } from "shared/config"
import { Attachment, AttributesObjectView, ContainerLoader, Status } from "shared/ui"

import { TestsTreeContext } from "widgets/tests"

import { TestResultComment } from "../comment"
import { TestResultSteps } from "../steps"
import styles from "./styles.module.css"

interface ResultListProps {
  testId: number
  testCase: TestCase
  isProjectArchive: boolean
}

const NoResults = () => {
  const { t } = useTranslation()

  return (
    <div style={{ padding: 8 }} id="test-result">
      <Typography>
        <Typography.Paragraph>
          <Typography.Text style={{ whiteSpace: "pre-wrap" }}>
            {t("No test results")}
          </Typography.Text>
        </Typography.Paragraph>
      </Typography>
    </div>
  )
}

export const ResultList = ({ testId, testCase, isProjectArchive }: ResultListProps) => {
  const { t } = useTranslation()
  const { testsTree } = useContext(TestsTreeContext)!
  const location = useLocation()
  const { projectId, testPlanId } = useParams<ParamProjectId & ParamTestPlanId>()
  const showArchive = useAppSelector(selectArchivedResultsIsShow)
  const drawerTest = useAppSelector(selectDrawerTest)

  const [getResults, { data: results, isFetching, isSuccess }] = useLazyGetResultsQuery()

  const handleRefetch = async () => {
    if (String(drawerTest?.plan) === String(testPlanId)) {
      await testsTree.current?.initRoot({ initParent: testPlanId })
      return
    }

    await testsTree.current?.refetchNodeBy((node) => node.id === drawerTest?.plan)
  }

  useEffect(() => {
    getResults({ testId: String(testId), showArchive, project: projectId ?? "" })
  }, [testId, showArchive])

  useEffect(() => {
    if (location.hash && isSuccess) {
      const element = document.getElementById(location.hash.substring(1))
      element?.scrollIntoView({ behavior: "smooth" })
    }
  }, [location, isSuccess])

  if (isFetching || !results) return <ContainerLoader />
  if (results.length === 0) return <NoResults />

  return (
    <div className={styles.resultList} id="test-result">
      {results.map((result) => {
        return (
          <div
            id={`result-${result.id}`}
            key={result.id}
            className={classNames(styles.resultListItem, {
              [styles.activeHashResult]: location.hash === `#result-${result.id}`,
            })}
          >
            <div className={styles.resultListHeader}>
              <div className={styles.resultListHeaderBase}>
                <Space>
                  <UserAvatar size={32} avatar_link={result.avatar_link} />
                  <p style={{ margin: 0, fontWeight: 500 }} id="test-result-username">
                    {result.user_full_name ? result.user_full_name : "-"}
                  </p>
                </Space>
              </div>
              <Space>
                {result.is_archive ? (
                  <div>
                    <Tag color={colors.error}>{t("Archived")}</Tag>
                  </div>
                ) : null}
                <div className={styles.resultListHeaderStatus}>
                  {result.status_text && (
                    <Status
                      name={result.status_text}
                      id={result.status}
                      color={result.status_color}
                    />
                  )}
                </div>
              </Space>
            </div>
            <div className={styles.resultListBody}>
              <TestResultComment result={result} />
              {!!result.steps_results.length && (
                <TestResultSteps stepsResult={result.steps_results} />
              )}
              <AttributesObjectView attributes={result.attributes} />
              {!!result.attachments.length && <Attachment.Field attachments={result.attachments} />}
            </div>
            <div className={styles.resultListFooter} data-testid="test-result-footer">
              <span>
                <HashLink
                  className={styles.link}
                  to={`/projects/${result.project}/plans/${testPlanId}/?test=${testId}#result-${result.id}`}
                  data-testid="test-result-footer-created-at"
                >
                  {dayjs(result.created_at).format("YYYY-MM-DD HH:mm")}
                </HashLink>
                <span className={styles.divider}>|</span>
                {result.test_case_version && (
                  <Link
                    className={styles.link}
                    to={`/projects/${result.project}/suites/${testCase.suite.id}/?test_case=${testCase.id}&version=${result.test_case_version}`}
                    data-testid="test-result-footer-version"
                  >
                    {t("ver.")} {result.test_case_version}
                  </Link>
                )}
              </span>
              <span>
                <EditCloneResult
                  isDisabled={isProjectArchive}
                  testCase={testCase}
                  testResult={result}
                  isClone
                  onSubmit={handleRefetch}
                />
                <span className={styles.divider}>|</span>
                <EditCloneResult
                  isDisabled={isProjectArchive}
                  testCase={testCase}
                  testResult={result}
                  isClone={false}
                  onSubmit={handleRefetch}
                />
              </span>
            </div>
          </div>
        )
      })}
    </div>
  )
}
