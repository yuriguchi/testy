import { CopyOutlined } from "@ant-design/icons"
import { Button, Form, Input, Modal } from "antd"
import { Controller } from "react-hook-form"
import { useTranslation } from "react-i18next"
import { useParams } from "react-router-dom"

import { useLazyGetTestSuitesQuery } from "entities/suite/api"

import { LazyNodeProps, LazyTreeNodeApi } from "shared/libs/tree"

import { BaseSearchEntity, LazyTreeSearch } from "widgets/lazy-tree-search/lazy-tree-search"

import { useTestCaseCopyModal } from "./use-test-case-copy-modal"

interface Props {
  testCase: TestCase
  onSubmit?: (suite: TestCase) => void
}

export const CopyTestCase = ({ testCase, onSubmit }: Props) => {
  const { t } = useTranslation()
  const { projectId } = useParams<ParamProjectId>()
  const [getSuites] = useLazyGetTestSuitesQuery()

  const { isShow, isLoading, control, formErrors, handleCancel, handleShow, handleSubmit } =
    useTestCaseCopyModal({ testCase, onSubmit })

  return (
    <>
      <Button id="copy-test-case" icon={<CopyOutlined />} onClick={handleShow}>
        {t("Copy")}
      </Button>
      <Modal
        className="copy-test-case-modal"
        title={`${t("Copy Test Case")} '${testCase.name}'`}
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
            onClick={handleSubmit}
            disabled={isLoading}
          >
            {t("Save")}
          </Button>,
        ]}
      >
        <Form id="copy-test-case-form" layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            label={t("New Test Case name")}
            validateStatus={formErrors?.newName ? "error" : ""}
            help={formErrors?.newName ? formErrors.newName.message : ""}
          >
            <Controller
              name="newName"
              control={control}
              render={({ field }) => (
                <Input
                  id="copy-test-case-name"
                  placeholder={t("Please enter a name")}
                  autoFocus
                  {...field}
                />
              )}
            />
          </Form.Item>
          <Form.Item
            label={t("Suite")}
            validateStatus={formErrors?.suite ? "error" : ""}
            help={formErrors?.suite ? formErrors.suite.message : ""}
          >
            <Controller
              name="suite"
              control={control}
              render={({ field }) => (
                <LazyTreeSearch
                  id="copy-test-case-select-suite"
                  // @ts-ignore
                  getData={getSuites}
                  skipInit={!isShow}
                  placeholder={t("Search a test suite")}
                  projectId={String(projectId)}
                  // @ts-ignore
                  onSelect={(node: LazyTreeNodeApi<BaseSearchEntity, LazyNodeProps> | null) =>
                    field.onChange(node ? { label: node.title, value: node.id as number } : null)
                  }
                  selectedId={field.value?.value}
                />
              )}
            />
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}
