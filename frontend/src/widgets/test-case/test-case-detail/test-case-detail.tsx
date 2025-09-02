import { Alert, Flex, Select, Typography } from "antd"
import { Controller } from "react-hook-form"
import { useTranslation } from "react-i18next"

import { TestCaseFields } from "entities/test-case/ui/test-case-fields"

import { CopyTestCase, DeleteTestCase, EditTestCase } from "features/test-case"
import { ArchiveTestCase } from "features/test-case/archive-test-case/archive-test-case"

import { ArchivedTag, Drawer } from "shared/ui"

import styles from "./styles.module.css"
import { TestCaseDetailTabs } from "./test-case-detail-tabs"
import { useTestCaseDetail } from "./use-test-case-detail"

export const TestCaseDetail = () => {
  const { t } = useTranslation()
  const {
    testCase,
    showVersion,
    versionData,
    control,
    isFetching,
    handleClose,
    handleChangeVersion,
    handleRestoreVersion,
    handleRefetch,
  } = useTestCaseDetail()

  const isLastVersion = testCase?.versions[0] === showVersion

  return (
    <Drawer
      id="drawer-test-case-details"
      title={
        testCase && (
          <Flex align="flex-start" style={{ width: "fit-content", marginRight: "auto" }}>
            <Flex gap={8}>
              {testCase.source_archived && (
                <Flex justify="center" align="center" style={{ height: 32 }}>
                  <ArchivedTag />
                </Flex>
              )}
              <Typography.Title level={3} className={styles.title}>
                {testCase.name}
              </Typography.Title>
            </Flex>
          </Flex>
        )
      }
      onClose={handleClose}
      isOpen={!!testCase}
      isLoading={isFetching}
      extra={
        testCase && (
          <Flex wrap gap={8} justify="flex-end">
            {!!testCase.versions && testCase.versions.length > 1 && (
              <Controller
                name="select"
                control={control}
                defaultValue={testCase.current_version}
                render={({ field }) => (
                  <Select
                    {...field}
                    placeholder={t("Version")}
                    style={{ minWidth: "100px" }}
                    options={versionData}
                    defaultValue={Number(testCase.current_version)}
                    onChange={handleChangeVersion}
                    value={showVersion}
                    data-testid="test-case-detail-version-select"
                  />
                )}
              />
            )}
            <CopyTestCase testCase={testCase} onSubmit={handleRefetch} />
            <EditTestCase testCase={testCase} />
            {!testCase.source_archived ? (
              <ArchiveTestCase testCase={testCase} onSubmit={handleRefetch} />
            ) : (
              <DeleteTestCase testCase={testCase} onSubmit={handleRefetch} />
            )}
          </Flex>
        )
      }
    >
      <>
        {testCase && !isLastVersion && (
          <Alert
            showIcon
            closable
            type="warning"
            description={
              <span>
                {t("Attention! This isn't the latest version.")}{" "}
                <a onClick={handleRestoreVersion}>{t("Restore")}</a>
              </span>
            }
            data-testid="test-case-detail-version-warning"
            style={{ marginBottom: 20 }}
          />
        )}
        {testCase && (
          <>
            <TestCaseFields testCase={testCase} />
            <TestCaseDetailTabs testCase={testCase} />
          </>
        )}
      </>
    </Drawer>
  )
}
