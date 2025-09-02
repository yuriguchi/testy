import { Button, Flex, Input, Space } from "antd"
import classNames from "classnames"
import { MeContext } from "processes"
import { useContext } from "react"
import { useTranslation } from "react-i18next"

import { ChangeLang } from "features/user"

import { icons } from "shared/assets/inner-icons"
import { Toggle } from "shared/ui"

import styles from "./styles.module.css"

const { ColumnViewIcon, TableIcon } = icons

interface Props {
  searchText: string
  onChangeSearch: (value: string) => void
  onIsOnlyFavoriteClick: (checked: boolean) => void
  onShowArchived: (checked: boolean) => void
  view: "cards" | "table"
  setView: (view: "cards" | "table") => void
}

export const DashboardHeader = ({
  searchText,
  onChangeSearch,
  onIsOnlyFavoriteClick,
  onShowArchived,
  view,
  setView,
}: Props) => {
  const { t } = useTranslation()
  const { userConfig } = useContext(MeContext)

  return (
    <div className={styles.header} data-testid="dashboard-header">
      <div data-testid="dashboard-header-search">
        <Input.Search
          placeholder={t("Search")}
          value={searchText}
          onChange={(e) => onChangeSearch(e.target.value)}
          style={{ maxWidth: 360 }}
          size="large"
          allowClear
          data-testid="dashboard-header-search-input"
        />
      </div>
      <Flex align="center" gap={16} className={styles.row}>
        <Toggle
          id="only-favorites-switcher"
          checked={userConfig?.projects?.is_only_favorite}
          onChange={onIsOnlyFavoriteClick}
          label={t("Favorites")}
          size="lg"
        />
        <Toggle
          id="show-archived-switcher"
          checked={userConfig?.projects?.is_show_archived}
          onChange={onShowArchived}
          label={t("Archives")}
          size="lg"
        />
      </Flex>
      <ChangeLang />
      <Space style={{ marginLeft: 16 }}>
        <Button
          className={classNames(styles.viewBtn, { [styles.viewBtnActive]: view === "cards" })}
          ghost={view !== "cards"}
          onClick={() => setView("cards")}
          icon={<ColumnViewIcon width={24} height={24} />}
          data-testid="dashboard-header-view-btn-cards"
        />
        <Button
          className={classNames(styles.viewBtn, { [styles.viewBtnActive]: view === "table" })}
          ghost={view !== "table"}
          onClick={() => setView("table")}
          icon={<TableIcon width={24} height={24} />}
          data-testid="dashboard-header-view-btn-table"
        />
      </Space>
    </div>
  )
}
