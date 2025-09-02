import { Button, Col, Flex, Form, Modal, Row, Tree, Typography } from "antd"
import { Controller } from "react-hook-form"
import { useTranslation } from "react-i18next"

import { useLazyGetTestPlanAncestorsQuery, useLazyGetTestPlansQuery } from "entities/test-plan/api"

import { ErrorObj } from "shared/hooks"
import { TreeUtils } from "shared/libs"
import {
  AlertError,
  ArchivedTag,
  ContainerLoader,
  DateFormItem,
  InputFormItem,
  TextAreaWithAttach,
} from "shared/ui"
import { LazyTreeSearchFormItem } from "shared/ui/form-items"

import { TestCaseLabels } from "../test-case-labels/test-case-labels"
import { useTestCasesFilter } from "../test-cases-filter/use-test-cases-filter"
import styles from "./styles.module.css"
import { UseTestPlanEditModalProps, useTestPlanEditModal } from "./use-test-plan-edit-modal"

// TODO looks like CreateTestPlanModal. Need refactoring
export const EditTestPlanModal = ({
  isShow,
  setIsShow,
  testPlan,
  onSubmit,
}: UseTestPlanEditModalProps) => {
  const { t } = useTranslation()
  const {
    errors,
    formErrors,
    control,
    selectedParent,
    treeData,
    searchText,
    expandedRowKeys,
    isDirty,
    isLoadingUpdate,
    isLoadingSearch,
    handleClose,
    handleRowExpand,
    handleSearch,
    handleSubmitForm,
    setDateFrom,
    setDateTo,
    disabledDateFrom,
    disabledDateTo,
    handleTestCaseChange,
    handleSelectTestPlan,
    selectedLables,
    labelProps,
    lableCondition,
    handleConditionClick,
    showArchived,
    handleToggleArchived,
    attachments,
    onLoad,
    setValue,
    setAttachments,
  } = useTestPlanEditModal({ isShow, setIsShow, testPlan, onSubmit })
  const [getPlans] = useLazyGetTestPlansQuery()
  const [getAncestors] = useLazyGetTestPlanAncestorsQuery()

  const { FilterButton, FilterForm } = useTestCasesFilter({
    labelProps,
    searchText,
    handleSearch,
    selectedLables,
    lableCondition,
    handleConditionClick,
    showArchived,
    handleToggleArchived,
  })

  return (
    <Modal
      className="test-plan-edit-modal"
      open={isShow}
      title={`${t("Edit")} ${t("Test Plan")} '${testPlan.name}'`}
      onCancel={handleClose}
      width="1100px"
      centered
      footer={[
        <Button id="close-test-plan-edit" key="back" onClick={handleClose}>
          {t("Close")}
        </Button>,
        <Button
          id="update-test-plan-edit"
          key="submit"
          type="primary"
          onClick={handleSubmitForm}
          loading={isLoadingUpdate}
          disabled={!isDirty}
        >
          {t("Update")}
        </Button>,
      ]}
    >
      {errors ? (
        <AlertError
          error={errors as ErrorObj}
          skipFields={["name", "parent", "test_cases", "started_at", "due_date"]}
        />
      ) : null}
      <Form id="test-plan-edit-form" layout="vertical" onFinish={handleSubmitForm}>
        <Row gutter={[32, 32]}>
          <Col span={12}>
            <InputFormItem
              id="edit-test-plan-name"
              control={control}
              name="name"
              label={t("Name")}
              maxLength={100}
              required
              formErrors={formErrors}
              externalErrors={errors}
            />
            <div className={styles.datesRow}>
              <DateFormItem
                id="edit-test-plan-start-date"
                control={control}
                label={t("Start date")}
                name="started_at"
                setDate={setDateFrom}
                disabledDate={disabledDateFrom}
                formStyles={{ width: "100%" }}
                formErrors={formErrors}
                externalErrors={errors}
                required
              />
              <span>-</span>
              <DateFormItem
                id="edit-test-plan-start-date"
                control={control}
                label={t("Due date")}
                name="due_date"
                setDate={setDateTo}
                disabledDate={disabledDateTo}
                formStyles={{ width: "100%" }}
                formErrors={formErrors}
                externalErrors={errors}
                required
              />
            </div>
            <LazyTreeSearchFormItem
              id="edit-test-plan-parent"
              control={control}
              name="parent"
              label={t("Parent plan")}
              placeholder={t("Search a test plan")}
              formErrors={formErrors}
              externalErrors={errors}
              // @ts-ignore
              getData={getPlans}
              // @ts-ignore
              getAncestors={getAncestors}
              rules={{
                validate: (value) =>
                  value !== testPlan.id || t("Test Plan cannot be its own parent."),
              }}
              skipInit={!isShow}
              selected={selectedParent}
              onSelect={handleSelectTestPlan}
            />
            <Form.Item
              label={t("Description")}
              validateStatus={errors?.description ? "error" : ""}
              help={errors?.description ? errors.description : ""}
            >
              <Controller
                name="description"
                control={control}
                render={({ field }) => (
                  <TextAreaWithAttach
                    uploadId="edit-test-plan-desc"
                    textAreaId="edit-test-plan-desc-textarea"
                    fieldProps={field}
                    stateAttachments={{ attachments, setAttachments }}
                    customRequest={onLoad}
                    setValue={setValue}
                  />
                )}
              />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              label={
                <div style={{ display: "flex" }}>
                  <Typography.Paragraph>{t("Test Cases")}</Typography.Paragraph>
                  {FilterButton}
                </div>
              }
              validateStatus={errors?.test_cases ? "error" : ""}
              help={errors?.test_cases ? errors.test_cases : ""}
            >
              <Controller
                name="test_cases"
                control={control}
                render={({ field }) => {
                  const onlyTestCases = field.value?.filter((tc) => !tc.startsWith("TS")) ?? []
                  return (
                    <>
                      {FilterForm}
                      {isLoadingSearch && <ContainerLoader />}
                      {!isLoadingSearch && (
                        <>
                          <Tree
                            {...field}
                            // @ts-ignore
                            titleRender={(node: TestPlan) => (
                              <>
                                <Flex gap={6} align="center">
                                  {node.is_archive && <ArchivedTag size="sm" />}
                                  {node.title}
                                </Flex>
                                {node?.labels ? <TestCaseLabels labels={node.labels} /> : null}
                              </>
                            )}
                            height={200}
                            virtual={false}
                            showIcon
                            checkable
                            selectable={false}
                            // @ts-ignore
                            treeData={TreeUtils.deleteChildren<TestPlan | Suite>(treeData)}
                            checkedKeys={field.value}
                            // eslint-disable-next-line @typescript-eslint/ban-ts-comment
                            //@ts-ignore
                            onCheck={handleTestCaseChange}
                            expandedKeys={expandedRowKeys}
                            onExpand={(_, record) => {
                              handleRowExpand(expandedRowKeys, String(record.node.key))
                            }}
                            className={styles.treeBlock}
                          />
                          <span style={{ opacity: 0.7, marginTop: 4 }}>
                            {t("Selected")}: {onlyTestCases.length} {t("Test Cases").toLowerCase()}
                          </span>
                        </>
                      )}
                    </>
                  )
                }}
              />
            </Form.Item>
          </Col>
        </Row>
      </Form>
    </Modal>
  )
}
