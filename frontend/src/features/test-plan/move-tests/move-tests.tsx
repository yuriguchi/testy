import { CopyOutlined } from "@ant-design/icons"
import { Alert, Button, Form, Modal } from "antd"
import { useTranslation } from "react-i18next"

import { useLazyGetTestPlanAncestorsQuery, useLazyGetTestPlansQuery } from "entities/test-plan/api"

import { LazyTreeSearchFormItem } from "shared/ui/form-items"

import { MoveTestsProps, useMoveTestsModal } from "./use-move-tests"

export const MoveTests = (props: MoveTestsProps) => {
  const { t } = useTranslation()
  const [getPlans] = useLazyGetTestPlansQuery()
  const [getAncestors] = useLazyGetTestPlanAncestorsQuery()

  const {
    isShow,
    handleCancel,
    handleShow,
    selectedPlan,
    handleSelectPlan,
    errors,
    formErrors,
    control,
    handleSubmitForm,
  } = useMoveTestsModal(props)

  return (
    <>
      <Button id="move-tests" icon={<CopyOutlined />} onClick={handleShow}>
        {t("Move tests")}
      </Button>
      <Modal
        className="move-tests-modal"
        title={t("Move test to plan")}
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
            loading={props.isLoading}
            onClick={handleSubmitForm}
          >
            {t("Save")}
          </Button>,
        ]}
      >
        <Form id="move-tests-form" layout="vertical" onFinish={handleSubmitForm}>
          <LazyTreeSearchFormItem
            id="move-tests-select"
            control={control}
            name="plan"
            label={t("Parent plan")}
            placeholder={t("Search a test plan")}
            formErrors={formErrors}
            externalErrors={errors}
            // @ts-ignore
            getData={getPlans}
            // @ts-ignore
            getAncestors={getAncestors}
            skipInit={!isShow}
            selected={selectedPlan}
            onSelect={handleSelectPlan}
          />
        </Form>
        {!!errors.length && (
          <Alert style={{ marginBottom: 0, marginTop: 16 }} description={errors} type="error" />
        )}
      </Modal>
    </>
  )
}
