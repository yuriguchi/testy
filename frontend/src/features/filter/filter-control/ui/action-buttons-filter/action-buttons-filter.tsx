import {
  CheckOutlined,
  CloseOutlined,
  CopyOutlined,
  DeleteOutlined,
  EditOutlined,
} from "@ant-design/icons"
import { Flex, Popover, Tooltip, notification } from "antd"
import classNames from "classnames"
import { MeContext } from "processes"
import { useContext, useState } from "react"
import { useTranslation } from "react-i18next"

import { ProjectContext } from "pages/project"

import { icons } from "shared/assets/inner-icons"
import { clearObject } from "shared/libs"

import styles from "./styles.module.css"

const { ContextMenuIcon, ResetIcon, SaveIcon } = icons

interface Props {
  type: "plans" | "suites"
  filterData: Record<string, unknown>
  filterSettings: FilterSettings
  onDelete: (name: string) => void
  updateSettings: (settings: Partial<FilterSettings>) => void
  resetFilterToSelected: () => void
  clearFilter: () => void
}

export const ActionButtonsFilter = ({
  type,
  filterData,
  filterSettings,
  onDelete,
  updateSettings,
  resetFilterToSelected,
  clearFilter,
}: Props) => {
  const { t } = useTranslation()

  const { userConfig, updateConfig } = useContext(MeContext)
  const { project } = useContext(ProjectContext)!
  const filtersKey = type === "plans" ? "test_plans" : "test_suites"
  const [isOpen, setIsOpen] = useState(false)

  const handleSaveChanges = async () => {
    if (!filterSettings.selected) {
      return
    }

    const clearedData = clearObject(filterData)
    const filterAsUrl = new URLSearchParams(clearedData as Record<string, string>)
    await updateConfig({
      ...userConfig,
      [filtersKey]: {
        ...userConfig?.[filtersKey],
        filters: {
          ...userConfig?.[filtersKey]?.filters,
          [project.id]: {
            ...userConfig?.[filtersKey]?.filters?.[project.id],
            [filterSettings.selected]: filterAsUrl.toString(),
          },
        },
      },
    })
    setIsOpen(false)
    notification.success({
      message: t("Success"),
      closable: true,
      description: t("Filter updated successfully"),
    })
  }

  const handleSaveAsNew = () => {
    updateSettings({
      editing: true,
      creatingNew: true,
      editingValue: filterSettings.selected ?? "",
    })
  }

  const handleNewNameAccept = () => {
    if (!filterSettings.editingValue.length) {
      notification.error({
        message: t("Error!"),
        description: t("Name filter cant be empty!"),
      })
      return
    }

    const isNew = filterSettings.creatingNew || !filterSettings.selected
    if (isNew) {
      saveAsNew()
    } else {
      renameFilter()
    }

    notification.success({
      message: t("Success"),
      closable: true,
      description: isNew ? t("Filter created successfully") : t("Filter updated successfully"),
    })

    updateSettings({
      selected: filterSettings.editingValue,
      editing: false,
      creatingNew: false,
      editingValue: "",
    })
    setIsOpen(false)
  }

  const handleNewNameClose = () => {
    updateSettings({ editing: false, editingValue: "" })
    setIsOpen(false)
  }

  const handleShowEdit = () => {
    updateSettings({
      editing: true,
      creatingNew: false,
      editingValue: filterSettings.selected ?? "",
    })
  }

  const saveAsNew = async () => {
    const clearedData = clearObject(filterData)
    const filterAsUrl = new URLSearchParams(clearedData as Record<string, string>)

    await updateConfig({
      ...userConfig,
      [filtersKey]: {
        ...userConfig?.[filtersKey],
        filters: {
          ...userConfig?.[filtersKey]?.filters,
          [project.id]: {
            ...userConfig?.[filtersKey]?.filters?.[project.id],
            [filterSettings.editingValue]: filterAsUrl.toString(),
          },
        },
      },
    })
  }

  const renameFilter = async () => {
    if (!filterSettings.selected) {
      return
    }

    const selectedFilterValue =
      userConfig?.[filtersKey]?.filters?.[project.id]?.[filterSettings.selected]
    const filtersObject = { ...userConfig?.[filtersKey]?.filters?.[project.id] }
    delete filtersObject[filterSettings.selected]

    await updateConfig({
      ...userConfig,
      [filtersKey]: {
        ...userConfig?.[filtersKey],
        filters: {
          ...userConfig?.[filtersKey]?.filters,
          [project.id]: {
            ...filtersObject,
            [filterSettings.editingValue]: selectedFilterValue,
          },
        },
      },
    })
  }

  if (filterSettings.editing) {
    return (
      <Flex style={{ marginLeft: "auto" }} gap={7}>
        <button
          className={classNames(styles.renameBtn, styles.saveRename)}
          onClick={handleNewNameAccept}
          data-testid="action-buttons-filter-rename-accept"
        >
          <CheckOutlined />
        </button>
        <button
          className={styles.renameBtn}
          onClick={handleNewNameClose}
          data-testid="action-buttons-filter-rename-close"
        >
          <CloseOutlined />
        </button>
      </Flex>
    )
  }

  if (filterSettings.selected) {
    return (
      <Flex gap={8}>
        {filterSettings.hasUnsavedChanges && (
          <Tooltip title={t("Reset filter")}>
            <button
              type="button"
              className={classNames("link-button", styles.actionBtn)}
              onClick={resetFilterToSelected}
              data-testid="action-buttons-filter-reset"
            >
              <ResetIcon />
            </button>
          </Tooltip>
        )}
        <Popover
          id="menu-filter"
          overlayInnerStyle={{ padding: "8px 0" }}
          content={
            <ul className={styles.filterMenuList}>
              {filterSettings.hasUnsavedChanges && (
                <li className={styles.filterMenuListItem} onClick={handleSaveChanges}>
                  <button
                    type="button"
                    className={styles.btn}
                    data-testid="action-buttons-filter-save-changes"
                  >
                    <CheckOutlined style={{ fontSize: 14 }} />
                  </button>
                  <span>{t("Save Changes")}</span>
                </li>
              )}
              <li className={styles.filterMenuListItem} onClick={handleSaveAsNew}>
                <button
                  type="button"
                  className={styles.btn}
                  data-testid="action-buttons-filter-save-as-new"
                >
                  <CopyOutlined style={{ fontSize: 14 }} />
                </button>
                <span>{t("Save as New Filter")}</span>
              </li>
              <li className={styles.filterMenuListItem} onClick={handleShowEdit}>
                <button
                  type="button"
                  className={styles.btn}
                  data-testid="action-buttons-filter-rename"
                >
                  <EditOutlined style={{ fontSize: 14 }} />
                </button>
                <span>{t("Rename")}</span>
              </li>
              <li
                className={classNames(styles.filterMenuListItem, styles.delete)}
                onClick={() => onDelete(filterSettings.selected ?? "")}
              >
                <button
                  type="button"
                  className={styles.btn}
                  data-testid="action-buttons-filter-delete"
                >
                  <DeleteOutlined style={{ fontSize: 14 }} />
                </button>
                <span>{t("Delete")}</span>
              </li>
            </ul>
          }
          placement="bottomRight"
          trigger="click"
          open={isOpen}
          onOpenChange={setIsOpen}
          arrow={false}
        >
          <button
            type="button"
            className={classNames("link-button", styles.actionBtn)}
            data-testid="action-buttons-filter-context-menu"
          >
            <ContextMenuIcon />
          </button>
        </Popover>
      </Flex>
    )
  }

  return (
    <Flex gap={8}>
      {filterSettings.hasUnsavedChanges && (
        <Tooltip title="Reset filter">
          <button
            type="button"
            className={classNames("link-button", styles.actionBtn)}
            onClick={clearFilter}
            data-testid="action-buttons-filter-reset"
          >
            <ResetIcon />
          </button>
        </Tooltip>
      )}
      <Tooltip title="Save filter" placement="bottomRight">
        <button
          type="button"
          className={classNames("link-button", styles.actionBtn)}
          onClick={handleShowEdit}
          data-testid="action-buttons-filter-save"
        >
          <SaveIcon />
        </button>
      </Tooltip>
    </Flex>
  )
}
