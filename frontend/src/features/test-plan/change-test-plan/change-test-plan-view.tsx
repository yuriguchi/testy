import { Flex, Form, Row, Tabs } from "antd"
import dayjs from "dayjs"
import { CustomAttributeAdd, CustomAttributeForm } from "entities/custom-attribute/ui"
import { Controller } from "react-hook-form"
import { useTranslation } from "react-i18next"

import { useLazyGetTestPlanAncestorsQuery, useLazyGetTestPlansQuery } from "entities/test-plan/api"

import { ErrorObj } from "shared/hooks"
import { AlertError, FormViewHeader, InputFormItem, TextAreaWithAttach } from "shared/ui"
import { DateFormItem, LazyTreeSearchFormItem, TreeSelectFormItem } from "shared/ui/form-items"

import styles from "./styles.module.css"
import { TestCasesFormItem } from "./ui"
import { useChangeTestPlan } from "./use-change-test-plan"

interface Props {
  type: "create" | "edit"
}

export const ChangeTestPlanView = ({ type }: Props) => {
  const { t } = useTranslation()
  const {
    control,
    formErrors,
    errors,
    tab,
    isDirty,
    isLoadingSubmit,
    selectedParent,
    attachments,
    // attachmentsIds,
    parametersTreeView,
    stateTestPlan,
    handleTabChange,
    handleCancel,
    handleSubmitForm,
    setDateFrom,
    disabledDateFrom,
    setDateTo,
    disabledDateTo,
    handleSelectTestPlan,
    setAttachments,
    // handleAttachmentChange,
    handleAttachmentLoad,
    // handleAttachmentRemove,
    setValue,
    // register,
    attributes,
    addAttribute,
    onAttributeChangeName,
    onAttributeChangeType,
    onAttributeChangeValue,
    onAttributeRemove,
  } = useChangeTestPlan({ type })

  const [getPlans] = useLazyGetTestPlansQuery()
  const [getAncestors] = useLazyGetTestPlanAncestorsQuery()

  const formTitle =
    type === "create"
      ? `${t("Create")} ${t("Test Plan")}`
      : `${t("Edit")} ${t("Test Plan")} '${stateTestPlan?.name}'`

  return (
    <>
      <FormViewHeader
        model="test-plan"
        type={type}
        title={formTitle}
        onClose={handleCancel}
        onSubmit={handleSubmitForm}
        isDisabledSubmit={!isDirty}
        isLoadingSubmit={isLoadingSubmit}
      />

      {errors ? (
        <AlertError
          error={errors as ErrorObj}
          style={{ marginTop: 12, marginBottom: 12 }}
          skipFields={[
            "name",
            "description",
            "parent",
            "parameters",
            "test_cases",
            "started_at",
            "due_date",
            "attributes",
          ]}
        />
      ) : null}
      <Form
        id={`test-plan-${type}-form`}
        layout="vertical"
        onFinish={handleSubmitForm}
        className={styles.form}
      >
        <Tabs defaultActiveKey="general" onChange={handleTabChange} activeKey={tab}>
          <Tabs.TabPane tab={t("General")} key="general">
            <Flex justify="space-between" gap={16} style={{ marginTop: 14 }}>
              <Flex vertical style={{ width: "40%" }}>
                <InputFormItem
                  id={`${type}-test-plan-name`}
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
                    id={`${type}-test-plan-start-date`}
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
                    id={`${type}-test-plan-due-date`}
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
                  id={`${type}-test-plan-parent`}
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
                  selected={selectedParent}
                  onSelect={handleSelectTestPlan}
                />
                {type === "create" && (
                  <TreeSelectFormItem
                    id={`${type}-test-plan-parameters`}
                    control={control}
                    name="parameters"
                    label={t("Parameters")}
                    treeData={parametersTreeView}
                    formErrors={formErrors}
                    externalErrors={errors}
                  />
                )}
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
                        uploadId={`${type}-test-plan-desc`}
                        textAreaId={`${type}-test-plan-desc-textarea`}
                        fieldProps={field}
                        stateAttachments={{ attachments, setAttachments }}
                        customRequest={handleAttachmentLoad}
                        setValue={setValue}
                      />
                    )}
                  />
                </Form.Item>
                <Controller
                  name="attributes"
                  control={control}
                  render={({ field }) => (
                    <Row style={{ flexDirection: "column" }}>
                      <CustomAttributeForm
                        attributes={attributes}
                        onChangeName={onAttributeChangeName}
                        onChangeType={onAttributeChangeType}
                        onChangeValue={onAttributeChangeValue}
                        onRemove={onAttributeRemove}
                        onBlur={field.onBlur}
                        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
                        errors={errors?.attributes ? JSON.parse(errors?.attributes) : undefined}
                      />
                      <CustomAttributeAdd onClick={addAttribute} />
                    </Row>
                  )}
                />
              </Flex>
              <Flex vertical style={{ width: "60%" }}>
                <TestCasesFormItem errors={errors} control={control} />
              </Flex>
            </Flex>
          </Tabs.TabPane>
          {/* <Tabs.TabPane tab={t("Attachments")} key="attachments">
            <Attachment.List
              handleAttachmentRemove={handleAttachmentRemove}
              attachments={attachments}
            />
            {attachmentsIds.map((field, index) => (
              <input type="hidden" key={field.id} {...register(`attachments.${index}`)} />
            ))}
            <Dragger
              name="file"
              multiple
              showUploadList={false}
              customRequest={handleAttachmentLoad}
              onChange={handleAttachmentChange}
              fileList={attachments}
              height={80}
            >
              <p className="ant-upload-text">
                {t("Drop files here to attach, or click to browse")}
              </p>
            </Dragger>
          </Tabs.TabPane> */}
        </Tabs>
      </Form>
    </>
  )
}
