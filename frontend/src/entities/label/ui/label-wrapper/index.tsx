import { DownOutlined } from "@ant-design/icons"
import { Input } from "antd"
import { useMemo, useRef } from "react"
import { useTranslation } from "react-i18next"

import { UseFormLabelsProps } from "entities/label/model"

import { colors } from "shared/config"
import { useOnClickOutside } from "shared/hooks"
import { HighLighterTesty } from "shared/ui"

import { Label } from "../label"
import styles from "./styles.module.css"

interface LabelWrapperProps {
  labelProps: UseFormLabelsProps
  fieldProps?: { onBlur: () => void }
  noAdding?: boolean
}

export const LabelWrapper = ({
  fieldProps,
  labelProps: {
    labels,
    searchValue,
    searchingLabels,
    setSearchValue,
    isShowPopup,
    setIsShowPopup,
    handleAddLabel,
    handleDeleteLabel,
    handleSubmitInput,
  },
  noAdding,
}: LabelWrapperProps) => {
  const { t } = useTranslation()
  const popupRef = useRef(null)
  useOnClickOutside(popupRef, () => setIsShowPopup(false))

  const handlePopupClick = () => {
    setIsShowPopup(!isShowPopup)
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.trimStart()
    setSearchValue(value)
  }

  const hasSearchingLabel = useMemo(() => {
    if (!searchValue.length) return true

    return searchingLabels.some((i) => i.name.toLowerCase() === searchValue.toLowerCase())
  }, [searchingLabels, searchValue])

  const isAlreadyAdded = useMemo(() => {
    if (!labels.length || !searchValue.length) return false

    if (labels.some((i) => i.name.toLowerCase() === searchValue.toLowerCase())) {
      return true
    }

    return false
  }, [labels, searchValue])

  return (
    <div className={styles.wrapper} data-testid="label-wrapper">
      <div className={styles.form}>
        <Input
          id="label-input"
          placeholder={t("New label")}
          suffix={
            <DownOutlined
              id="label-input-arrow"
              style={{ cursor: "pointer" }}
              onClick={handlePopupClick}
            />
          }
          value={searchValue}
          onChange={handleInputChange}
          onKeyDown={(e) => handleSubmitInput(e, searchValue)}
          onBlur={fieldProps?.onBlur}
          data-testid="label-wrapper-input"
        />
        {isShowPopup && (
          <div
            id="label-popup"
            className={styles.popup}
            ref={popupRef}
            data-testid="label-wrapper-popup"
          >
            <ul>
              {searchingLabels.map((label) => (
                <li
                  key={label.id}
                  onClick={() => handleAddLabel(label.name)}
                  data-testid={`label-wrapper-label-${label.name}`}
                >
                  <HighLighterTesty searchWords={searchValue} textToHighlight={label.name} />
                </li>
              ))}
              {isAlreadyAdded && (
                <>
                  <div className={styles.line} />
                  <span
                    className={styles.newLabel}
                    onClick={() => handleAddLabel(searchValue)}
                    data-testid="label-wrapper-already-added"
                  >
                    <HighLighterTesty searchWords={searchValue} textToHighlight={searchValue} />(
                    {t("Already added")})
                  </span>
                </>
              )}
              {!hasSearchingLabel && !isAlreadyAdded && !noAdding && (
                <>
                  <div className={styles.line} />
                  <span
                    className={styles.newLabel}
                    onClick={() => handleAddLabel(searchValue)}
                    data-testid="label-wrapper-new-label"
                  >
                    <HighLighterTesty searchWords={searchValue} textToHighlight={searchValue} />(
                    {t("New label")})
                  </span>
                </>
              )}
            </ul>
          </div>
        )}
      </div>
      {!!labels.length && (
        <ul id="label-list" className={styles.list}>
          {labels.map((label) => (
            <li key={label.id}>
              <Label
                content={label.name}
                onDelete={() => handleDeleteLabel(label.name)}
                color={colors.accent}
              />
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
