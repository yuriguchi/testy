import { Button, Col, Flex, Form, Modal, Row, Tree, Typography } from "antd"
import dayjs from "dayjs"
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
  TreeSelectFormItem,
} from "shared/ui"
import { LazyTreeSearchFormItem } from "shared/ui/form-items"

import { TestCaseLabels } from "../test-case-labels/test-case-labels"
import { useTestCasesFilter } from "../test-cases-filter/use-test-cases-filter"
import styles from "./styles.module.css"
import { useTestPlanCreateModal } from "./use-test-plan-create-modal"

interface CreateTestPlanModalProps {
  isShow: boolean
  setIsShow: React.Dispatch<React.SetStateAction<boolean>>
  testPlan?: TestPlan
  onSubmit?: (plan: TestPlan) => void
}

// TODO looks like EditTestPlanModal. Need refactoring
export const CreateTestPlanModal = ({
  isShow,
  setIsShow,
  testPlan,
  onSubmit,
}: CreateTestPlanModalProps) => {
  const { t } = useTranslation()
  const {
    isLoadingCreateTestPlan,
    isLoadingTreeData,
    errors,
    formErrors,
    control,
    searchText,
    treeData,
    parametersTreeView,
    expandedRowKeys,
    isDirty,
    selectedParent,
    handleRowExpand,
    setDateFrom,
    setDateTo,
    disabledDateFrom,
    disabledDateTo,
    handleSubmitForm,
    handleClose,
    handleSearch,
    handleTestCaseChange,
    handleSelectTestPlan,
    selectedLables,
    labelProps,
    lableCondition,
    handleConditionClick,
    showArchived,
    handleToggleArchived,
    attachments,
    setAttachments,
    onLoad,
    setValue,
  } = useTestPlanCreateModal({
    isShow,
    setIsShow,
    testPlan,
    onSubmit,
  })
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
      className="test-plan-create-modal"
      title={`${t("Create")} ${t("Test Plan")}`}
      open={isShow}
      onCancel={handleClose}
      width="1100px"
      centered
      footer={[
        <Button id="close-test-plan-create" key="back" onClick={handleClose}>
          {t("Close")}
        </Button>,
        <Button
          id="create-test-plan-create"
          key="submit"
          type="primary"
          loading={isLoadingCreateTestPlan}
          onClick={handleSubmitForm}
          disabled={!isDirty}
        >
          {t("Create")}
        </Button>,
      ]}
    >
      {errors ? (
        <AlertError
          error={errors as ErrorObj}
          skipFields={[
            "name",
            "description",
            "parent",
            "parameters",
            "test_cases",
            "started_at",
            "due_date",
          ]}
        />
      ) : null}

      <Form
        id="test-plan-create-form"
        layout="vertical"
        onFinish={handleSubmitForm}
        className={styles.form}
      >
        <Row gutter={[32, 32]}>
          <Col span={12}>
            <InputFormItem
              id="create-test-plan-name"
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
                id="create-test-plan-start-date"
                control={control}
                label={t("Start date")}
                name="started_at"
                setDate={setDateFrom}
                disabledDate={disabledDateFrom}
                formStyles={{ width: "100%" }}
                formErrors={formErrors}
                externalErrors={errors}
                defaultDate={dayjs()}
                required
              />
              <span>-</span>
              <DateFormItem
                id="create-test-plan-due-date"
                control={control}
                label={t("Due date")}
                name="due_date"
                setDate={setDateTo}
                disabledDate={disabledDateTo}
                formStyles={{ width: "100%" }}
                formErrors={formErrors}
                externalErrors={errors}
                defaultDate={dayjs().add(1, "day")}
                required
              />
            </div>
            <LazyTreeSearchFormItem
              id="create-test-plan-parent"
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
                    uploadId="create-test-plan-desc"
                    textAreaId="create-test-plan-desc-textarea"
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
            <TreeSelectFormItem
              id="create-test-plan-parameters"
              control={control}
              name="parameters"
              label={t("Parameters")}
              treeData={parametersTreeView}
              formErrors={formErrors}
              externalErrors={errors}
            />
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
                  const testCases = field.value.filter((item: string) => !item.startsWith("TS"))
                  return (
                    <>
                      {FilterForm}
                      {isLoadingTreeData && <ContainerLoader />}
                      {!isLoadingTreeData && (
                        <>
                          <Tree
                            {...field}
                            //@ts-ignore
                            titleRender={(node: TestPlan) => {
                              return (
                                <>
                                  <Flex gap={6} align="center">
                                    {node.is_archive && <ArchivedTag size="sm" />}
                                    {node.title}
                                  </Flex>
                                  {node.labels ? <TestCaseLabels labels={node.labels} /> : null}
                                </>
                              )
                            }}
                            height={200}
                            virtual={false}
                            showIcon
                            checkable
                            selectable={false}
                            //@ts-ignore
                            treeData={TreeUtils.deleteChildren<Suite>(treeData)}
                            checkedKeys={field.value}
                            // @ts-ignore
                            onCheck={handleTestCaseChange}
                            expandedKeys={expandedRowKeys}
                            onExpand={(_, record) => {
                              handleRowExpand(expandedRowKeys, String(record.node.key))
                            }}
                            className={styles.treeBlock}
                          />
                          <span style={{ opacity: 0.7, marginTop: 4 }}>
                            {t("Selected")}: {testCases.length} {t("Test Cases").toLowerCase()}
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
