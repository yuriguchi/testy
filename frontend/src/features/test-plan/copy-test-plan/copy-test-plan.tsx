import { CopyOutlined } from "@ant-design/icons"
import { Alert, Button, Checkbox, Form, Input, Modal } from "antd"
import dayjs from "dayjs"
import { ReactNode, memo } from "react"
import { Controller } from "react-hook-form"
import { useTranslation } from "react-i18next"
import { useParams } from "react-router-dom"

import { useLazyGetTestPlanAncestorsQuery, useLazyGetTestPlansQuery } from "entities/test-plan/api"

import { DateFormItem } from "shared/ui"
import { LazyTreeSearchFormItem } from "shared/ui/form-items"

import styles from "./styles.module.css"
import { useTestPlanCopyModal } from "./use-copy-test-plan"

interface Props {
  as?: ReactNode
  testPlan: TestPlan
  onSubmit?: (plan: TestPlan) => void
}

export const CopyTestPlan = memo(({ as, testPlan, onSubmit }: Props) => {
  const { t } = useTranslation()
  const { projectId } = useParams<ParamProjectId>()
  const [getPlans] = useLazyGetTestPlansQuery()
  const [getAncestors] = useLazyGetTestPlanAncestorsQuery()

  const {
    isShow,
    isLoading,
    handleCancel,
    handleShow,
    selectedPlan,
    handleSelectPlan,
    errors,
    formErrors,
    control,
    handleSubmitForm,
    isDisabled,
    setDateFrom,
    setDateTo,
    disabledDateFrom,
    disabledDateTo,
  } = useTestPlanCopyModal({ testPlan, onSubmit })

  return (
    <>
      {as ? (
        <div id="copy-test-plan" onClick={handleShow}>
          {as}
        </div>
      ) : (
        <Button id="copy-test-plan" icon={<CopyOutlined />} onClick={handleShow}>
          {t("Copy")}
        </Button>
      )}
      <Modal
        className="copy-test-plan-modal"
        // eslint-disable-next-line @typescript-eslint/restrict-template-expressions
        title={`${t("Copy Test Plan")} '${testPlan.name}'`}
        open={isShow}
        onCancel={handleCancel}
        centered
        footer={[
          <Button id="cancel-btn" key="back" onClick={handleCancel}>
            {t("Cancel")}
          </Button>,
          <Button
            id="save-btn"
            key="submit"
            type="primary"
            loading={isLoading}
            onClick={handleSubmitForm}
            disabled={isDisabled}
          >
            {t("Save")}
          </Button>,
        ]}
      >
        <Form id="copy-test-plan-form" layout="vertical" onFinish={handleSubmitForm}>
          <Form.Item label={t("New Plan name")}>
            <Controller
              name="new_name"
              control={control}
              render={({ field }) => (
                <Input
                  id="copy-test-plan-form-name"
                  placeholder={t("Please enter a name")}
                  {...field}
                  autoFocus
                />
              )}
            />
          </Form.Item>
          <LazyTreeSearchFormItem
            id="copy-test-plan-select"
            control={control}
            // @ts-ignore
            name="parent"
            label={t("Parent plan")}
            placeholder={t("Search a test plan")}
            formErrors={formErrors}
            externalErrors={errors}
            // @ts-ignore
            getData={getPlans}
            // @ts-ignore
            getAncestors={getAncestors}
            dataParams={{
              project: projectId,
            }}
            skipInit={!isShow}
            selected={selectedPlan}
            onSelect={handleSelectPlan}
          />
          <div className={styles.datesRow}>
            <DateFormItem
              id="copy-test-plan-start-date"
              control={control}
              label={t("Start date")}
              name="startedAt"
              setDate={setDateFrom}
              disabledDate={disabledDateFrom}
              formStyles={{ width: "100%" }}
              formErrors={formErrors}
              externalErrors={errors}
              defaultDate={dayjs()}
            />
            <span>-</span>
            <DateFormItem
              id="copy-test-plan-due-date"
              control={control}
              label={t("Due date")}
              name="dueDate"
              setDate={setDateTo}
              disabledDate={disabledDateTo}
              formStyles={{ width: "100%" }}
              formErrors={formErrors}
              externalErrors={errors}
              defaultDate={dayjs().add(1, "day")}
            />
          </div>
          <Form.Item name={t("Keep Assignee")}>
            <Controller
              name="keepAssignee"
              control={control}
              render={({ field }) => (
                <Checkbox
                  {...field}
                  checked={field.value}
                  onChange={(e) => field.onChange(e.target.checked)}
                >
                  {t("Include Test Cases Assignment")}
                </Checkbox>
              )}
            />
          </Form.Item>
        </Form>
        {!!errors.length && (
          <Alert style={{ marginBottom: 0, marginTop: 16 }} description={errors} type="error" />
        )}
      </Modal>
    </>
  )
})

CopyTestPlan.displayName = "CopyTestPlan"
