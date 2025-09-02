import { Flex, Typography } from "antd"
import classNames from "classnames"
import { useEffect, useRef, useState } from "react"
import { useTranslation } from "react-i18next"

import { colors } from "shared/config"
import { Markdown } from "shared/ui"

import styles from "./styles.module.css"

const renderAttributeValue = (value: string | string[] | object) => {
  if (typeof value === "string") {
    return <Markdown content={value} />
  } else if (Array.isArray(value)) {
    return <Markdown content={value.join("\r\n")} />
  } else {
    return JSON.stringify(value, null, 2)
  }
}

interface Props {
  title: string
  value: string | string[] | object
  isRequired?: boolean
}

export const CustomAttributeInTab = ({ title, value, isRequired }: Props) => {
  const { t } = useTranslation()
  const [isExpanded, setIsExpanded] = useState(false)
  const [isOverflowing, setIsOverflowing] = useState(false)
  const contentRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (contentRef.current) {
      setIsOverflowing(contentRef.current.scrollHeight > 100)
    }
  }, [])

  const toggleExpand = () => {
    setIsExpanded((prev) => !prev)
  }

  return (
    <Flex vertical className={styles.wrapper}>
      <Flex>
        <Typography.Title id="attribute-name" level={4} className={styles.title}>
          {title}
        </Typography.Title>
        {isRequired && <span className={styles.requireIcon}>*</span>}
      </Flex>
      <Typography.Text
        id="attribute-value"
        style={{ whiteSpace: "pre-wrap" }}
        className={classNames(styles.value, { [styles.expanded]: isExpanded })}
        ref={contentRef}
      >
        {renderAttributeValue(value)}
      </Typography.Text>
      {isOverflowing && (
        <button
          data-testid="attribute-show-more-btn"
          style={{ color: colors.accent, cursor: "pointer", marginTop: 8 }}
          onClick={toggleExpand}
          className={styles.showMore}
        >
          {isExpanded ? t("Hide more") : t("Show more")}
        </button>
      )}
    </Flex>
  )
}
