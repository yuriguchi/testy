import { DeleteOutlined } from "@ant-design/icons"
import { Button, Col, Flex, Input, Tooltip } from "antd"
import cn from "classnames"
import classNames from "classnames"
import { Noop } from "react-hook-form"
import { useTranslation } from "react-i18next"

import { colors } from "shared/config"
import { FontsIcon, JsonIcon, ListIcon } from "shared/ui/icons"

import styles from "./styles.module.css"

const { TextArea } = Input

interface Props {
  index: number
  attribute: Attribute
  onChangeName: (id: string, name: string) => void
  onChangeType: (id: string, type: AttributeType) => void
  onChangeValue: (id: string, value: string) => void
  onRemove: (id: string) => void
  errorName?: string
  errorValue?: string
  onBlur?: Noop
}

export const CustomAttributeFormItem = ({
  errorName,
  errorValue,
  index,
  attribute,
  onChangeName,
  onChangeType,
  onChangeValue,
  onRemove,
  onBlur,
}: Props) => {
  const { t } = useTranslation()

  return (
    <div id={`attribute-block-${index}`}>
      <Flex wrap style={{ rowGap: 8, columnGap: 8, paddingBottom: 5 }}>
        <Col flex="auto">
          {(attribute.is_init || !!attribute.required) && (
            <div className="ant-col ant-form-item-label">
              <label
                className={classNames(styles.label, {
                  [styles.labelIsRequired]: !!attribute.required,
                })}
                title={attribute.name}
              >
                {attribute.name} ({attribute.type})
              </label>
            </div>
          )}
          {!attribute.is_init && !attribute.required && (
            <Input
              id={`attribute-name-${index}`}
              value={attribute.name}
              onChange={(e) => onChangeName(attribute.id, e.target.value)}
              onBlur={onBlur}
              style={{ borderColor: errorName?.length ? colors.error : "" }}
              disabled={attribute.required}
              placeholder={t("Attribute name")}
            />
          )}
        </Col>

        {!attribute.is_init && !attribute.required && (
          <Flex align="center">
            <Tooltip placement="topRight" title={t("Text value")}>
              <Button
                id={`attribute-type-text-${index}`}
                disabled={attribute.is_init}
                icon={<FontsIcon />}
                onClick={() => onChangeType(attribute.id, "Text")}
                type="text"
                className={classNames(styles.buttonType, {
                  [styles.active]: attribute.type === "Text",
                  [styles.disabled]: attribute.is_init,
                })}
              />
            </Tooltip>

            <Tooltip placement="topRight" title={t("List value")}>
              <Button
                id={`attribute-type-list-${index}`}
                disabled={attribute.is_init}
                icon={<ListIcon />}
                onClick={() => onChangeType(attribute.id, "List")}
                type="text"
                className={classNames(styles.buttonType, {
                  [styles.active]: attribute.type === "List",
                  [styles.disabled]: attribute.is_init,
                })}
              />
            </Tooltip>

            <Tooltip placement="topRight" title={t("JSON value")}>
              <Button
                id={`attribute-type-json-${index}`}
                disabled={attribute.is_init}
                icon={<JsonIcon />}
                onClick={() => onChangeType(attribute.id, "JSON")}
                type="text"
                className={classNames(styles.buttonType, {
                  [styles.active]: attribute.type === "JSON",
                  [styles.disabled]: attribute.is_init,
                })}
                style={{ marginRight: 16 }}
              />
            </Tooltip>

            <Tooltip placement="topRight" title={t("Delete attribute")}>
              <Button
                id={`attribute-type-json-${index}`}
                disabled={attribute.required ?? attribute.is_init}
                danger
                type="text"
                icon={<DeleteOutlined />}
                onClick={() => onRemove(attribute.id)}
                style={{ marginLeft: "auto" }}
                className={classNames(styles.buttonType, {
                  [styles.disabled]: attribute.required,
                })}
              />
            </Tooltip>
          </Flex>
        )}
      </Flex>

      <TextArea
        id={`attribute-value-${index}`}
        className={cn({ [`attribute-value-${index}-req`]: !!attribute.required })}
        rows={4}
        value={String(attribute.value)}
        onChange={(e) => onChangeValue(attribute.id, e.target.value)}
        onBlur={onBlur}
        style={{ borderColor: errorValue?.length ? colors.error : "" }}
      />
    </div>
  )
}
