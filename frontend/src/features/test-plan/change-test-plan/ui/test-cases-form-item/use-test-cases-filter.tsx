import { FilterFilled, FilterOutlined } from "@ant-design/icons"
import { Switch, Typography } from "antd"
import Search from "antd/lib/input/Search"
import cn from "classnames"
import { useState } from "react"
import { useTranslation } from "react-i18next"

import { UseFormLabelsProps } from "entities/label/model"
import { LabelWrapper } from "entities/label/ui"

import styles from "./styles.module.css"

interface TestCasesFilterProps {
  searchText: string
  handleSearch: (value: string, labels: number[], labels_condition: LabelCondition) => Promise<void>
  selectedLables: number[]
  lableCondition: LabelCondition
  handleConditionClick: () => void
  labelProps: UseFormLabelsProps
  showArchived: boolean
  handleToggleArchived: () => void
}

export const useTestCasesFilter = ({
  labelProps,
  searchText,
  handleSearch,
  selectedLables,
  lableCondition,
  handleConditionClick,
  showArchived,
  handleToggleArchived,
}: TestCasesFilterProps) => {
  const { t } = useTranslation()
  const [isShow, setIsShow] = useState(false)

  const handleClick = () => {
    setIsShow(!isShow)
  }

  const FilterBtn = (
    <div id="test-cases-filter-btn" onClick={handleClick} className={styles.filterBtn}>
      {isShow ? <FilterFilled /> : <FilterOutlined />}
    </div>
  )

  const Form = isShow && (
    <div className={styles.form}>
      <div className={styles.row}>
        <Typography.Text>{t("Name")}</Typography.Text>
        <Search
          placeholder={t("Search")}
          onChange={(e) => handleSearch(e.target.value, selectedLables, lableCondition)}
          value={searchText}
          className={styles.search}
          data-testid="test-cases-filter-search"
        />
      </div>
      <div className={cn(styles.row, styles.rowWithThree)}>
        <Typography.Text>{t("Labels")}</Typography.Text>
        <LabelWrapper labelProps={labelProps} noAdding />
        <Switch
          checkedChildren={t("or")}
          unCheckedChildren={t("and")}
          defaultChecked
          className={styles.switcher}
          checked={lableCondition === "or"}
          onChange={handleConditionClick}
          disabled={selectedLables.length < 2}
          data-testid="test-cases-filter-switcher"
        />
      </div>
      <div className={styles.archivedRow}>
        <Typography.Text>{t("Show Archived")}</Typography.Text>
        <Switch
          checkedChildren={t("yes")}
          unCheckedChildren={t("no")}
          defaultChecked
          className={styles.switcher}
          checked={showArchived}
          onChange={handleToggleArchived}
          data-testid="test-cases-filter-switcher-archived"
        />
      </div>
    </div>
  )

  return {
    FilterButton: FilterBtn,
    FilterForm: Form,
  }
}
