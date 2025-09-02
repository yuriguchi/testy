import {
  CopyOutlined,
  DeleteOutlined,
  EditOutlined,
  HistoryOutlined,
  PlusOutlined,
} from "@ant-design/icons"
import { Flex } from "antd"
import { MenuProps } from "antd/lib"
import { useTranslation } from "react-i18next"
import { Link } from "react-router-dom"

import { ChangeTestSuite, CopySuite, DeleteSuite } from "features/suite"
import { CreateTestCase } from "features/test-case"
import { ArchiveTestPlan, ChangeTestPlan, CopyTestPlan, DeleteTestPlan } from "features/test-plan"

import { icons } from "shared/assets/inner-icons"
import { LazyNodeProps, LazyTreeApi } from "shared/libs/tree"

import {
  refetchNodeAfterArchive,
  refetchNodeAfterCreateOrCopy,
  refetchNodeAfterDelete,
} from "./utils"

const { ArchiveIcon } = icons

export interface TestPlanProps {
  data: TestPlan
  type: "plans"
  projectId: number
  tree: LazyTreeApi<TestPlan, LazyNodeProps>
}

export interface TestSuiteProps {
  data: Suite
  type: "suites"
  projectId: number
  tree: LazyTreeApi<Suite, LazyNodeProps>
}

export function useTreebarNodeContextMenu(
  props: TestPlanProps | TestSuiteProps
): MenuProps["items"] {
  const { t } = useTranslation()
  const refetchParentAfterCreateOrCopy = (updatedEntity: BaseEntity) => {
    refetchNodeAfterCreateOrCopy(props.tree, updatedEntity)
  }

  const refetchParentAfterArchive = (updatedEntity: BaseEntity) => {
    refetchNodeAfterArchive(props.tree, updatedEntity)
  }

  const refetchParentAfterDelete = (updatedEntity: BaseEntity) => {
    refetchNodeAfterDelete(props.tree, updatedEntity)
  }

  if (props.type === "plans") {
    return [
      {
        label: (
          <ChangeTestPlan
            type="create"
            as={
              <Flex gap={6} align="center">
                <PlusOutlined style={{ fontSize: 14 }} /> {t("Create child plan")}
              </Flex>
            }
            testPlan={props.data}
          />
        ),
        key: "create_child_plan",
      },
      {
        label: (
          <CopyTestPlan
            as={
              <Flex gap={6} align="center">
                <CopyOutlined style={{ fontSize: 14 }} />
                {t("Copy")}
              </Flex>
            }
            testPlan={props.data}
            onSubmit={refetchParentAfterCreateOrCopy}
          />
        ),
        key: "copy_plan",
      },
      !props.data.is_archive && {
        label: (
          <ChangeTestPlan
            type="edit"
            as={
              <Flex gap={6} align="center">
                <EditOutlined style={{ fontSize: 14 }} />
                {t("Edit")}
              </Flex>
            }
            testPlan={props.data}
          />
        ),
        key: "edit_plan",
      },
      !props.data.is_archive && {
        label: (
          <ArchiveTestPlan
            as={
              <Flex gap={6} align="center">
                <ArchiveIcon width={14} height={14} /> {t("Archive")}
              </Flex>
            }
            testPlan={props.data}
            onSubmit={refetchParentAfterArchive}
          />
        ),
        key: "archive_plan",
      },
      {
        label: (
          <DeleteTestPlan
            as={
              <Flex gap={6} align="center">
                <DeleteOutlined style={{ fontSize: 14 }} />
                {t("Delete")}
              </Flex>
            }
            testPlan={props.data}
            onSubmit={refetchParentAfterDelete}
          />
        ),
        key: "delete_plan",
      },
      {
        type: "divider",
      },
      {
        label: (
          <Link
            to={`/projects/${props.projectId}/plans/${props.data.id}/activity`}
            style={{ gap: 6, display: "flex", flexDirection: "row", alignItems: "center" }}
          >
            <HistoryOutlined style={{ fontSize: 14 }} /> {t("View activity")}
          </Link>
        ),
        key: "view_activity",
      },
    ].filter(Boolean) as MenuProps["items"]
  }

  return [
    {
      label: (
        <ChangeTestSuite
          type="create"
          as={
            <Flex gap={6} align="center">
              <PlusOutlined style={{ fontSize: 14 }} />
              {t("Create child suite")}
            </Flex>
          }
          suite={props.data}
        />
      ),
      key: "create_child_suite",
    },
    {
      label: (
        <CopySuite
          as={
            <Flex gap={6} align="center">
              <CopyOutlined style={{ fontSize: 14 }} />
              {t("Copy")}
            </Flex>
          }
          suite={props.data}
          onSubmit={refetchParentAfterCreateOrCopy}
        />
      ),
      key: "copy_suite",
    },
    {
      label: (
        <ChangeTestSuite
          type="edit"
          as={
            <Flex gap={6} align="center">
              <EditOutlined style={{ fontSize: 14 }} />
              {t("Edit")}
            </Flex>
          }
          suite={props.data}
        />
      ),
      key: "edit_suite",
    },
    {
      label: (
        <DeleteSuite
          as={
            <Flex gap={6} align="center">
              <DeleteOutlined style={{ fontSize: 14 }} />
              {t("Delete")}
            </Flex>
          }
          suite={props.data}
          onSubmit={refetchParentAfterDelete}
        />
      ),
      key: "delete_suite",
    },
    {
      type: "divider",
    },
    {
      label: (
        <CreateTestCase
          as={
            <Flex gap={6} align="center">
              <PlusOutlined style={{ fontSize: 14 }} />
              {t("Create Test Case")}
            </Flex>
          }
          parentSuiteId={props.data.id}
        />
      ),
      key: "create_test_case",
    },
  ]
}
