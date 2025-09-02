import { Pagination } from "antd"
import dayjs from "dayjs"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Link } from "react-router-dom"

import { useGetTestCaseHistoryChangesQuery } from "entities/test-case/api"

import { UserAvatar, UserUsername } from "entities/user/ui"

import { ContainerLoader } from "shared/ui"

import styles from "./styles.module.css"

export const TestCaseHistoryChanges = ({ testCase }: { testCase: TestCase }) => {
  const { t } = useTranslation()
  const [pagination, setPagination] = useState({
    page: 1,
    page_size: 5,
  })

  const { data, isLoading } = useGetTestCaseHistoryChangesQuery({
    testCaseId: testCase.id,
    page: pagination.page,
    page_size: pagination.page_size,
  })

  const handlePaginationChange = (page: number, page_size: number) => {
    setPagination({ page, page_size })
  }

  if (isLoading || !data) return <ContainerLoader />

  return (
    <>
      <ul style={{ paddingLeft: 8 }}>
        {data.results.map((history, index) => (
          <li className={styles.item} key={index}>
            <div className={styles.userInfo}>
              <div style={{ display: "flex", marginRight: 4 }}>
                <UserAvatar size={32} avatar_link={history.user?.avatar_link ?? null} />
              </div>
              <UserUsername username={history.user?.username ?? "unknown"} />
              <div className={styles.info}>
                <span style={{ fontWeight: 500 }}>{history.action.toLowerCase()}</span> a test case
                <span>at {dayjs(history.history_date).format("DD MMM YYYY HH:mm")}</span>|
                <Link
                  to={`/projects/${testCase.project}/suites/${testCase.suite.id}?version=${history.version}&test_case=${testCase.id}`}
                  id={`${history.version}-${index}`}
                >
                  {t("ver.")} {history.version}
                </Link>
              </div>
            </div>
          </li>
        ))}
      </ul>
      <Pagination
        defaultCurrent={1}
        pageSize={pagination.page_size}
        size="small"
        total={data.count}
        style={{ width: "fit-content", marginLeft: "auto" }}
        onChange={handlePaginationChange}
      />
    </>
  )
}
