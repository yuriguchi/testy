import { Modal, notification } from "antd"
import { useContext, useEffect, useMemo, useState } from "react"
import { useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"
import { useParams, useSearchParams } from "react-router-dom"

import { useAppDispatch, useAppSelector } from "app/hooks"

import { useLazyGetTestCaseByIdQuery, useRestoreTestCaseMutation } from "entities/test-case/api"
import { selectDrawerTestCase, setDrawerTestCase } from "entities/test-case/model"

import { initInternalError } from "shared/libs"
import { AlertSuccessChange } from "shared/ui"

import { TestCasesTreeContext } from "../test-cases-tree"

export const useTestCaseDetail = () => {
  const { t } = useTranslation()
  const { testSuiteId } = useParams<ParamTestSuiteId>()
  const { testCasesTree } = useContext(TestCasesTreeContext)!

  const dispatch = useAppDispatch()
  const drawerTestCase = useAppSelector(selectDrawerTestCase)
  const [searchParams, setSearchParams] = useSearchParams()
  const version = searchParams.get("version")
  const testCaseId = searchParams.get("test_case")
  const [showVersion, setShowVersion] = useState<number | null>(null)
  const { control } = useForm()

  const [getTestCaseById, { isFetching }] = useLazyGetTestCaseByIdQuery()
  const [restoreTestCase] = useRestoreTestCaseMutation()

  const fetchTestCase = async (newTestCaseId: string, newVersion?: string) => {
    try {
      const res = await getTestCaseById({
        testCaseId: newTestCaseId,
        version: newVersion,
      }).unwrap()
      dispatch(setDrawerTestCase(res))
    } catch (err: unknown) {
      initInternalError(err)
    }
  }

  useEffect(() => {
    if (!drawerTestCase) {
      return
    }
    setShowVersion(Number(drawerTestCase.current_version))
  }, [drawerTestCase])

  useEffect(() => {
    if (!testCaseId || drawerTestCase) {
      return
    }

    fetchTestCase(String(testCaseId), version ?? undefined)
  }, [testCaseId, drawerTestCase, version])

  useEffect(() => {
    return () => {
      dispatch(setDrawerTestCase(null))
    }
  }, [])

  const versionData = useMemo(() => {
    if (!drawerTestCase?.versions) {
      return []
    }
    const sorted = [...drawerTestCase.versions].sort((a, b) => b - a)
    return sorted.map((item) => ({
      value: item,
      // eslint-disable-next-line @typescript-eslint/restrict-template-expressions
      label: `${t("ver.")} ${item}`,
    }))
  }, [drawerTestCase])

  const handleClose = () => {
    searchParams.delete("test_case")
    searchParams.delete("version")
    setSearchParams(searchParams)
    dispatch(setDrawerTestCase(null))
  }

  const handleChangeVersion = async (newVersion: number) => {
    setShowVersion(newVersion)
    searchParams.set("version", String(newVersion))
    setSearchParams(searchParams)
    await fetchTestCase(String(testCaseId), String(newVersion))
  }

  const handleRestoreVersion = () => {
    if (!showVersion || !drawerTestCase) return
    Modal.confirm({
      title: t("Do you want to restore this version of test case?"),
      okText: t("Restore"),
      cancelText: t("Cancel"),
      onOk: async () => {
        try {
          const res = await restoreTestCase({
            testCaseId: drawerTestCase.id,
            version: showVersion,
          }).unwrap()
          setSearchParams({
            version: String(res.versions[0]),
            test_case: String(drawerTestCase.id),
          })
          notification.success({
            message: t("Success"),
            closable: true,
            description: (
              <AlertSuccessChange
                id={String(drawerTestCase.id)}
                action="restore"
                title={t("Test Case")}
                link={`/projects/${drawerTestCase.project}/suites/${drawerTestCase.suite.id}?version=${res.versions[0]}&test_case=${drawerTestCase.id}`}
              />
            ),
          })
        } catch (err: unknown) {
          initInternalError(err)
        }
      },
      okButtonProps: { "data-testid": "restore-test-case-button-confirm" },
      cancelButtonProps: { "data-testid": "restore-test-case-button-cancel" },
    })
  }

  const handleRefetch = async (testCase: TestCase) => {
    if (!testCasesTree.current) {
      return
    }

    if (String(testSuiteId) === String(testCase.suite.id)) {
      await testCasesTree.current.initRoot()
      return
    }

    await testCasesTree.current?.refetchNodeBy((node) => node.id === testCase.suite.id)
  }

  return {
    testCase: drawerTestCase,
    showVersion,
    versionData,
    control,
    isFetching,
    handleClose,
    handleChangeVersion,
    handleRestoreVersion,
    handleRefetch,
  }
}
