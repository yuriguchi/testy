import { SearchOutlined } from "@ant-design/icons"
import { Button, Input, Space } from "antd"
import type { FilterConfirmProps, FilterDropdownProps } from "antd/es/table/interface"
import { useEffect, useState } from "react"
import { useTranslation } from "react-i18next"

import { colors } from "shared/config"
import { HighLighterTesty } from "shared/ui"

import { useDebounce } from "./use-debounce"

export const useTableSearch = (debounceTime = 300, defaultValue?: string) => {
  const { t } = useTranslation()
  const [searchText, setSearchText] = useState(defaultValue ?? "")
  const [searchedColumn, setSearchedColumn] = useState<string[]>([])
  const searchDebounce = useDebounce(searchText, debounceTime)

  useEffect(() => {
    if (defaultValue !== undefined && defaultValue !== searchText) {
      setSearchedColumn([])
      setSearchText(defaultValue)
    }
  }, [defaultValue])

  const handleSearch = (
    selectedKeys: string[],
    confirm: (param?: FilterConfirmProps) => void,
    dataIndex: string
  ) => {
    confirm()
    setSearchText(selectedKeys[0])
    setSearchedColumn((prevState) => [...prevState, dataIndex])
  }

  const getColumnSearch = (dataIndex: string) => ({
    filterDropdown: ({ setSelectedKeys, selectedKeys, confirm, close }: FilterDropdownProps) => (
      <div style={{ padding: 8 }} onKeyDown={(e) => e.stopPropagation()}>
        <Input
          placeholder={t("Search")}
          value={selectedKeys[0] as string}
          onChange={(e) => setSelectedKeys(e.target.value ? [e.target.value] : [])}
          onPressEnter={() => handleSearch(selectedKeys as string[], confirm, dataIndex)}
          style={{ marginBottom: 8, display: "block" }}
          defaultValue={defaultValue}
          data-testid={`${dataIndex}-search-input`}
        />
        <Space style={{ display: "flex", justifyContent: "right" }}>
          <Button
            id="close-search"
            size="small"
            type="text"
            onClick={() => {
              close()
            }}
            data-testid={`${dataIndex}-search-close`}
          >
            {t("Close")}
          </Button>
          <Button
            id="submit-search"
            size="small"
            type="primary"
            onClick={() => handleSearch(selectedKeys as string[], confirm, dataIndex)}
            data-testid={`${dataIndex}-search-submit`}
          >
            {t("Search")}
          </Button>
        </Space>
      </div>
    ),
    filterIcon: (filtered: boolean) => (
      <SearchOutlined
        style={{ color: filtered ? colors.accent : undefined }}
        data-testid={`${dataIndex}-search-icon`}
      />
    ),
    render: (text: string) =>
      searchedColumn.some((i) => i === dataIndex) ? (
        <HighLighterTesty searchWords={searchText} textToHighlight={text} />
      ) : (
        text
      ),
  })

  const onClear = () => {
    setSearchText("")
    setSearchedColumn([])
  }

  return {
    setSearchText,
    setSearchedColumn,
    getColumnSearch,
    onClear,
    searchText,
    searchedColumn,
    searchDebounce,
  }
}
