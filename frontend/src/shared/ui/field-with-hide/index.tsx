import { Col, Divider, Row } from "antd"
import { useMemo, useState } from "react"
import { useTranslation } from "react-i18next"

import { colors } from "shared/config"

import { Markdown } from ".."

interface Props {
  id?: string
  title: string
  value: string
}

export const FieldWithHide = ({ id, title, value }: Props) => {
  const { t } = useTranslation()

  const valueLines = useMemo(() => {
    return value.split(/\r\n|\r|\n/) ?? []
  }, [value])

  const shortValue = useMemo(() => {
    const text = valueLines.slice(0, 3).join("\n")
    if (valueLines.length > 3 || text.length > 300) return `${text.slice(0, 300)}...`
    return text
  }, [valueLines])
  const [isShowMore, setIsShowMore] = useState(false)

  const handleShowMoreClick = () => {
    setIsShowMore((prevState) => !prevState)
  }

  return (
    <>
      <Divider orientation="left" style={{ margin: 0 }} orientationMargin={0}>
        {title}
      </Divider>

      <Row align="middle" id={id}>
        <Col flex="auto">
          <div style={{ padding: 8 }}>
            <Markdown content={isShowMore ? value : shortValue} />
            {(valueLines.length > 3 || value.length > 300) && (
              <span
                style={{ color: colors.accent, cursor: "pointer" }}
                onClick={handleShowMoreClick}
              >
                {isShowMore ? t("Hide more") : t("Show more")}
              </span>
            )}
          </div>
        </Col>
      </Row>
    </>
  )
}
