import { useEffect, useState } from "react"
import { useSearchParams } from "react-router-dom"

import { useAppDispatch, useAppSelector } from "app/hooks"

import { useGetTestQuery } from "entities/test/api"

import { useGetTestCaseByIdQuery } from "entities/test-case/api"

import {
  selectArchivedResultsIsShow,
  selectTests,
  showArchivedResults,
} from "entities/test-plan/model"

import { selectDrawerTest, setDrawerTest } from "./slice"

type TabTypes = "results" | "comments"

export const useTestDetail = () => {
  const dispatch = useAppDispatch()
  const [tab, setTab] = useState<TabTypes>("results")
  const [commentOrdering, setCommentOrdering] = useState<"asc" | "desc">("desc")
  const tests = useAppSelector(selectTests)
  const drawerTest = useAppSelector(selectDrawerTest)

  const [testCaseData, setTestCaseData] = useState<TestCase | null>(null)
  const [searchParams, setSearchParams] = useSearchParams()
  const testId = searchParams.get("test")

  const { data: testCase, isFetching: isFetchingTestCase } = useGetTestCaseByIdQuery(
    { testCaseId: String(drawerTest?.case) },
    {
      skip: !drawerTest,
    }
  )

  const { data: testData, isFetching: isFetchingTest } = useGetTestQuery(testId ?? "", {
    skip: !testId || !!drawerTest,
  })

  const showArchive = useAppSelector(selectArchivedResultsIsShow)

  const handleShowArchived = () => {
    dispatch(showArchivedResults())
  }

  const handleCloseDetails = () => {
    searchParams.delete("test")
    setSearchParams(searchParams)
    dispatch(setDrawerTest(null))
  }

  const handleTabChange = (activeKey: string) => {
    setTab(activeKey as TabTypes)
  }

  const handleCommentOrderingClick = () => {
    setCommentOrdering(commentOrdering === "asc" ? "desc" : "asc")
  }

  useEffect(() => {
    const selectedCase = tests.find((t) => t.case === testCase?.id)

    if (selectedCase && testCase) {
      const updated = {
        ...testCase,
        test_suite_description: selectedCase.test_suite_description,
      }
      setTestCaseData(updated)
      return
    }
    setTestCaseData(testCase ?? null)
  }, [testCase, tests])

  useEffect(() => {
    if (!testData || !testId || !!drawerTest) {
      return
    }

    dispatch(setDrawerTest(testData))
  }, [testData, testId, drawerTest])

  useEffect(() => {
    return () => {
      dispatch(setDrawerTest(null))
    }
  }, [])

  return {
    drawerTest,
    testCase: testCaseData,
    isFetching: isFetchingTestCase || isFetchingTest,
    showArchive,
    commentOrdering,
    tab,
    handleShowArchived,
    handleCloseDetails,
    handleTabChange,
    handleCommentOrderingClick,
  }
}
