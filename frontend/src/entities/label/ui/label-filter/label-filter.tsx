import classNames from "classnames"
import { useContext, useEffect, useRef, useState } from "react"
import { useTranslation } from "react-i18next"

import { useGetLabelsQuery } from "entities/label/api"

import { ProjectContext } from "pages/project"

import { colors } from "shared/config"

import { Label } from "../label"
import { SkeletonLabelFilter } from "./skeleton-label-filter"
import styles from "./styles.module.css"

export interface LabelFilterValue {
  labels: number[]
  not_labels: number[]
  labels_condition: LabelCondition
}

interface Props {
  value: LabelFilterValue
  onChange: (value: LabelFilterValue) => void
}

export const LabelFilter = ({ value, onChange }: Props) => {
  const { t } = useTranslation()
  const { project } = useContext(ProjectContext)!
  const { data, isLoading } = useGetLabelsQuery({ project: project.id.toString() })

  const [showAll, setShowAll] = useState(false)
  const [isOverflowing, setIsOverflowing] = useState(false)
  const listRef = useRef<HTMLUListElement>(null)

  const handleLableClick = (label: LabelInForm) => {
    const labelId = Number(label.id)
    const findLabel = value.labels.find((i) => i === labelId)
    const findNotLabel = value.not_labels.find((i) => i === labelId)

    if (!findLabel && !findNotLabel) {
      const newState = { ...value, labels: [...value.labels, labelId] }
      onChange(newState)
      return
    }

    if (findLabel) {
      const newState = {
        ...value,
        labels: value.labels.filter((i) => i !== labelId),
        not_labels: [...value.not_labels, labelId],
      }
      onChange(newState)
      return
    }

    if (findNotLabel) {
      const newState: LabelFilterValue = {
        ...value,
        labels: value.labels.filter((i) => i !== labelId),
        not_labels: value.not_labels.filter((i) => i !== labelId),
      }
      onChange(newState)
      return
    }
  }

  const handleShowMore = () => {
    setShowAll(true)
    setIsOverflowing(false)
  }

  useEffect(() => {
    if (!listRef.current || !data?.length) {
      return
    }

    const checkOverflow = () => {
      setIsOverflowing(listRef.current!.scrollHeight > 52) // 52px = two rows
    }
    checkOverflow()

    const resizeObserver = new ResizeObserver(checkOverflow)
    resizeObserver.observe(listRef.current)

    return () => resizeObserver.disconnect()
  }, [data])

  if (isLoading) {
    return <SkeletonLabelFilter />
  }

  if (!data?.length) {
    return <span className={styles.noData}>{t("No data")}</span>
  }

  return (
    <>
      <ul
        ref={listRef}
        id="label-filter"
        className={classNames(styles.list, { [styles.maxSize]: showAll })}
      >
        {(data ?? []).map((label) => {
          const hasInLabels = value.labels.some((i) => i === label.id)
          const hasInNotLabels = value.not_labels.some((i) => i === label.id)
          const color = hasInLabels ? colors.accent : hasInNotLabels ? "line-through" : undefined

          return (
            <li key={label.id} data-testid={`label-filter-label-${label.name}`}>
              <Label content={label.name} color={color} onClick={() => handleLableClick(label)} />
            </li>
          )
        })}
      </ul>
      {isOverflowing && !showAll && (
        <button
          type="button"
          className={classNames("link-button", styles.showMore)}
          onClick={handleShowMore}
          data-testid="label-filter-show-more"
        >
          {t("Show more")}
        </button>
      )}
    </>
  )
}
