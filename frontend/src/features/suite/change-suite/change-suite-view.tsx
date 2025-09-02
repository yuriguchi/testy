import { Flex, Form, Row, Tabs } from "antd"
import { CustomAttributeAdd, CustomAttributeForm } from "entities/custom-attribute/ui"
import { Controller } from "react-hook-form"
import { useTranslation } from "react-i18next"

import { useLazyGetTestSuiteAncestorsQuery, useLazyGetTestSuitesQuery } from "entities/suite/api"

import { ErrorObj } from "shared/hooks"
import { AlertError, FormViewHeader, InputFormItem, TextAreaWithAttach } from "shared/ui"
import { LazyTreeSearchFormItem } from "shared/ui/form-items"

import styles from "./styles.module.css"
import { useChangeTestSuite } from "./use-change-suite"

interface Props {
  type: "create" | "edit"
}

export const ChangeTestSuiteView = ({ type }: Props) => {
  const { t } = useTranslation()
  const {
    control,
    formErrors,
    errors,
    tab,
    isLoadingSubmit,
    isDirty,
    attachments,
    // attachmentsIds,
    selectedParent,
    stateTestSuite,
    // register,
    setAttachments,
    handleCancel,
    handleSubmitForm,
    handleTabChange,
    handleAttachmentLoad,
    // handleAttachmentChange,
    // handleAttachmentRemove,
    handleSelectTestSuite,
    setValue,
    attributes,
    addAttribute,
    onAttributeChangeName,
    onAttributeChangeType,
    onAttributeChangeValue,
    onAttributeRemove,
  } = useChangeTestSuite({ type })

  const [getSuites] = useLazyGetTestSuitesQuery()
  const [getAncestors] = useLazyGetTestSuiteAncestorsQuery()

  const formTitle =
    type === "create"
      ? `${t("Create")} ${t("Test Suite")}`
      : `${t("Edit")} ${t("Test Suite")} '${stateTestSuite?.name}'`

  return (
    <>
      <FormViewHeader
        model="test-suite"
        type={type}
        title={formTitle}
        isDisabledSubmit={!isDirty}
        isLoadingSubmit={isLoadingSubmit}
        onClose={handleCancel}
        onSubmit={handleSubmitForm}
      />

      {errors ? (
        <AlertError
          error={errors as ErrorObj}
          style={{ marginTop: 12, marginBottom: 12 }}
          skipFields={["name", "description", "parent", "attributes"]}
        />
      ) : null}
      <Form
        id={`test-suite-${type}-form`}
        layout="vertical"
        onFinish={handleSubmitForm}
        className={styles.form}
      >
        <Tabs defaultActiveKey="general" onChange={handleTabChange} activeKey={tab}>
          <Tabs.TabPane tab={t("General")} key="general">
            <Flex justify="space-between" gap={16} style={{ marginTop: 14 }}>
              <Flex vertical style={{ width: "100%" }}>
                <InputFormItem
                  id={`${type}-test-suite-name`}
                  control={control}
                  name="name"
                  required
                  label={t("Name")}
                  maxLength={100}
                  formErrors={formErrors}
                  externalErrors={errors}
                />
                <LazyTreeSearchFormItem
                  id={`${type}-test-suite-parent`}
                  control={control}
                  // @ts-ignore
                  name="parent"
                  label={t("Parent Test Suite")}
                  placeholder={t("Search a test suite")}
                  formErrors={formErrors}
                  externalErrors={errors}
                  // @ts-ignore
                  getData={getSuites}
                  // @ts-ignore
                  getAncestors={getAncestors}
                  selected={selectedParent}
                  onSelect={handleSelectTestSuite}
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
                        uploadId={`${type}-test-suite-desc`}
                        textAreaId={`${type}-test-suite-desc-textarea`}
                        fieldProps={field}
                        stateAttachments={{ attachments, setAttachments }}
                        customRequest={handleAttachmentLoad}
                        setValue={setValue}
                      />
                    )}
                  />
                </Form.Item>
              </Flex>
              <Flex vertical style={{ width: "100%" }}>
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
