import { CopyOutlined } from "@ant-design/icons"
import { Alert, Button, Flex, Form, Input, Select } from "antd"
import { ReactNode, memo } from "react"
import { Controller } from "react-hook-form"
import { useTranslation } from "react-i18next"

import { useLazyGetTestSuiteAncestorsQuery, useLazyGetTestSuitesQuery } from "entities/suite/api"

import { LazyTreeSearchFormItem } from "shared/ui/form-items"
import { WindowDefaultBar } from "shared/ui/window/default/window-default-bar/window-default-bar"
import { Window } from "shared/ui/window/window"
import { WindowBar } from "shared/ui/window/window-bar"
import { WindowContent } from "shared/ui/window/window-content"
import { WindowTrigger } from "shared/ui/window/window-trigger"

import { useSuiteCopyModal } from "./use-suite-copy-modal"

interface Props {
  as?: ReactNode
  suite: Suite
  onSubmit?: (newSuite: CopySuiteResponse) => void
}

export const CopySuite = memo(({ as, suite, onSubmit }: Props) => {
  const { t } = useTranslation()
  const [getSuites] = useLazyGetTestSuitesQuery()
  const [getAncestors] = useLazyGetTestSuiteAncestorsQuery()

  const {
    errors,
    formErrors,
    isShow,
    isLoading,
    projects,
    isDisabled,
    control,
    selectedSuite,
    selectedProject,
    handleSubmitForm,
    handleSelectSuite,
    handleChangeShow,
    handleShow,
    handleCancel,
  } = useSuiteCopyModal(suite, onSubmit)

  return (
    <Window
      open={isShow}
      onOpenChange={handleChangeShow}
      defaultSize={{ width: 500, height: "auto" }}
      minSize={{ width: 400, height: 400 }}
    >
      <WindowTrigger asChild>
        {as ? (
          <div id="copy-test-suite" onClick={handleShow}>
            {as}
          </div>
        ) : (
          <Button id="copy-test-suite" icon={<CopyOutlined />} onClick={handleShow}>
            {t("Copy").toUpperCase()}
          </Button>
        )}
      </WindowTrigger>
      <WindowContent>
        <WindowBar>
          {({ hide, expand, onHide, onExpand, onClose }) => (
            <WindowDefaultBar
              onClose={onClose}
              onExpand={onExpand}
              onHide={onHide}
              title={`${t("Copy Test Suite")} '${suite.name}'`}
              expand={expand}
              hide={hide}
            />
          )}
        </WindowBar>
        <Form id="create-test-suite-form" layout="vertical" onFinish={handleSubmitForm}>
          <Form.Item label={t("New Suite name")}>
            <Controller
              name="new_name"
              control={control}
              render={({ field }) => (
                <Input
                  id="copy-test-suite-form-name"
                  placeholder={t("Please enter a name")}
                  {...field}
                  autoFocus
                />
              )}
            />
          </Form.Item>
          <Form.Item label={t("Project")}>
            <Controller
              name="project"
              control={control}
              render={({ field }) => (
                <Select
                  {...field}
                  id="copy-test-suite-select-project"
                  showSearch
                  placeholder={t("Please select project")}
                  notFoundContent={t("No matches")}
                  defaultActiveFirstOption={false}
                  labelInValue
                  style={{ width: "100%" }}
                  options={projects}
                  value={selectedProject}
                  filterOption={(input, option) =>
                    (option?.label ?? "").toLowerCase().includes(input.toLowerCase())
                  }
                  filterSort={(optionA, optionB) =>
                    (optionA?.label ?? "")
                      .toLowerCase()
                      .localeCompare((optionB?.label ?? "").toLowerCase())
                  }
                />
              )}
            />
          </Form.Item>
          <LazyTreeSearchFormItem
            id="copy-test-suite-select-suite"
            control={control}
            name="suite"
            label={t("Suite")}
            placeholder={t("Search a test suite")}
            formErrors={formErrors}
            // @ts-ignore
            getData={getSuites}
            // @ts-ignore
            getAncestors={getAncestors}
            dataParams={{
              project: String(selectedProject?.value),
            }}
            skipInit={!isShow}
            selected={selectedSuite}
            onSelect={handleSelectSuite}
          />
          <Flex align="center" justify="flex-end" gap={8} style={{ marginTop: 16 }}>
            <Button id="cancel-btn" key="back" onClick={handleCancel}>
              {t("Cancel")}
            </Button>
            <Button
              id="save-btn"
              key="submit"
              type="primary"
              loading={isLoading}
              onClick={handleSubmitForm}
              disabled={isDisabled}
            >
              {t("Save")}
            </Button>
          </Flex>
        </Form>
        {!!errors.length && (
          <Alert style={{ marginBottom: 0, marginTop: 16 }} description={errors} type="error" />
        )}
      </WindowContent>
    </Window>
  )
})

CopySuite.displayName = "CopySuite"
