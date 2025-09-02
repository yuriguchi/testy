import { CheckOutlined, CloseOutlined, DeleteOutlined, EditOutlined } from "@ant-design/icons"
import { Flex, Input, InputRef, Popover, notification } from "antd"
import classNames from "classnames"
import { MeContext } from "processes"
import { ChangeEvent, useContext, useEffect, useMemo, useRef, useState } from "react"
import { useTranslation } from "react-i18next"

import { ProjectContext } from "pages/project"

import { icons } from "shared/assets/inner-icons"
import { deepEqualObjects } from "shared/libs"
import { QuryParamsSchema, queryParamsBySchema } from "shared/libs/query-params"

import styles from "./styles.module.css"

const { ArrowIcon } = icons

interface Props {
  type: "plans" | "suites"
  filterData: Record<string, unknown>
  filterSettings: FilterSettings
  configFilters: Record<string, string> | undefined
  filterSchema: QuryParamsSchema
  onDelete: (name: string) => void
  onSelect: (name: string) => void
  updateSettings: (settings: Partial<FilterSettings>) => void
}

export const SelectFilter = ({
  type,
  filterData,
  filterSettings,
  configFilters,
  filterSchema,
  onDelete,
  onSelect,
  updateSettings,
}: Props) => {
  const { t } = useTranslation()

  const { userConfig, updateConfig } = useContext(MeContext)
  const { project } = useContext(ProjectContext)!

  const filtersKey = type === "plans" ? "test_plans" : "test_suites"
  const [isOpen, setIsOpen] = useState(false)
  const [editingItems, setEditingItems] = useState<Record<string, string>>({})

  const editInputRef = useRef<InputRef | null>(null)

  const configFiltersKeys = useMemo(() => {
    if (!configFilters) {
      return []
    }

    return Object.keys(configFilters)
  }, [configFilters])

  const handleOpenChange = (toggle: boolean) => {
    if (!configFiltersKeys.length || filterSettings.editing) {
      return
    }

    setIsOpen(toggle)
  }

  const handleSelect = (name: string) => {
    updateSettings({ selected: name })
    onSelect(name)
    setIsOpen(false)
  }

  const handleShowEdit = (name: string) => {
    setEditingItems((prev) => ({ ...prev, [name]: name }))
  }

  const handleChangeEditValue = (e: ChangeEvent<HTMLInputElement>) => {
    updateSettings({ editingValue: e.target.value })
  }

  const handleChangeItemEditValue = (name: string, value: string) => {
    setEditingItems((prev) => ({ ...prev, [name]: value }))
  }

  const handleSaveItemValue = async (oldName: string) => {
    const newName = editingItems[oldName]
    if (!newName.length) {
      notification.error({
        message: t("Error!"),
        description: t("Name filter cant be empty!"),
      })
      return
    }

    const selectedFilterValue = userConfig?.[filtersKey]?.filters?.[project.id]?.[oldName]
    const filtersObject = { ...userConfig?.[filtersKey]?.filters?.[project.id] }
    delete filtersObject[oldName]

    await updateConfig({
      ...userConfig,
      [filtersKey]: {
        ...userConfig?.[filtersKey],
        filters: {
          [project.id]: {
            ...filtersObject,
            [newName]: selectedFilterValue,
          },
        },
      },
    })

    const editItems = { ...editingItems }
    delete editItems[oldName]
    setEditingItems(editItems)

    notification.success({
      message: t("Success"),
      closable: true,
      description: t("Filter updated successfully"),
    })

    if (oldName === filterSettings.selected) {
      updateSettings({ selected: newName })
    }
  }

  const handleCloseEditingItemValue = (name: string) => {
    const editItems = { ...editingItems }
    delete editItems[name]
    setEditingItems(editItems)
  }

  useEffect(() => {
    if (filterSettings.editing) {
      editInputRef.current?.focus()
    }
  }, [filterSettings.editing])

  useEffect(() => {
    if (!filterSettings.selected) {
      return
    }

    const savedFilterValue =
      userConfig?.[filtersKey]?.filters?.[project.id]?.[filterSettings.selected]
    if (!savedFilterValue) {
      updateSettings({ hasUnsavedChanges: false })
      return
    }

    const parsedSavedFilterValue = queryParamsBySchema(filterSchema, {
      url: savedFilterValue,
    })

    const isEqualObject = deepEqualObjects(parsedSavedFilterValue, filterData)
    if (isEqualObject) {
      updateSettings({ hasUnsavedChanges: false })
      return
    }

    updateSettings({ hasUnsavedChanges: true })
  }, [filterSettings.selected, filterData, userConfig])

  if (filterSettings.editing) {
    return (
      <Input
        ref={editInputRef}
        className={styles.input}
        variant="borderless"
        placeholder={t("Filter name")}
        value={filterSettings.editingValue}
        onChange={handleChangeEditValue}
        data-testid="select-filter-input-editing"
      />
    )
  }

  if (!configFiltersKeys.length) {
    return (
      <h3 className={styles.title} data-testid="select-filter-title-new-filter">
        {t("New Filter")}
      </h3>
    )
  }

  return (
    <Popover
      id="select-filter-popover"
      overlayInnerStyle={{ padding: "8px 0" }}
      content={
        <ul className={styles.list} data-testid="select-filter-list">
          {configFiltersKeys.map((filterName, index) => {
            const id = `${filterName}-${index}`

            if (Object.keys(editingItems).includes(filterName)) {
              return (
                <li key={id} className={styles.itemEditing}>
                  <Input
                    className={styles.itemInput}
                    variant="borderless"
                    placeholder={t("Filter name")}
                    value={editingItems[filterName] ?? filterName}
                    autoFocus
                    onChange={(e) => handleChangeItemEditValue(filterName, e.target.value)}
                    data-testid={`select-filter-input-${filterName}`}
                  />
                  <Flex style={{ marginLeft: "auto" }} gap={7}>
                    <button
                      className={classNames(styles.btn, styles.saveRename)}
                      onClick={() => handleSaveItemValue(filterName)}
                      data-testid={`select-filter-save-rename-${filterName}`}
                    >
                      <CheckOutlined />
                    </button>
                    <button
                      className={classNames(styles.btn, styles.closeRename)}
                      onClick={() => handleCloseEditingItemValue(filterName)}
                      data-testid={`select-filter-close-rename-${filterName}`}
                    >
                      <CloseOutlined />
                    </button>
                  </Flex>
                </li>
              )
            }

            return (
              <li
                id={id}
                key={id}
                className={classNames(styles.item, {
                  [styles.active]: filterSettings.selected === filterName,
                })}
                onClick={(e) => {
                  e.preventDefault()
                  handleSelect(filterName)
                }}
              >
                {filterName}
                <div className={styles.btns}>
                  <button
                    className={styles.btn}
                    onClick={(e) => {
                      e.stopPropagation()
                      handleShowEdit(filterName)
                    }}
                    data-testid={`select-filter-edit-${filterName}`}
                  >
                    <EditOutlined style={{ fontSize: 14 }} />
                  </button>
                  <button
                    className={classNames(styles.btn, styles.deleteBtn)}
                    onClick={(e) => {
                      e.stopPropagation()
                      onDelete(filterName)
                    }}
                    data-testid={`select-filter-delete-${filterName}`}
                  >
                    <DeleteOutlined style={{ fontSize: 14 }} />
                  </button>
                </div>
              </li>
            )
          })}
        </ul>
      }
      placement="bottomLeft"
      trigger="click"
      open={!configFiltersKeys.length || filterSettings.editing ? false : isOpen}
      onOpenChange={handleOpenChange}
      arrow={false}
      className={classNames({
        [styles.disabled]: !configFiltersKeys.length || filterSettings.editing,
      })}
    >
      <div className={styles.titleBlock}>
        {!filterSettings.editing && (
          <h3 className={styles.title} data-testid="select-filter-title">
            {filterSettings.selected ?? t("New Filter")}
          </h3>
        )}
        {!!configFiltersKeys.length && !filterSettings.editing && (
          <ArrowIcon width={24} height={24} data-testid="select-filter-arrow" />
        )}
      </div>
      {filterSettings.hasUnsavedChanges && (
        <span className={styles.unsaved} data-testid="select-filter-unsaved-changes">
          {t("Unsaved Changes")}
        </span>
      )}
    </Popover>
  )
}
