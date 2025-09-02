import { Button, Col, Divider, Flex, Input, Radio, Tooltip, Typography } from "antd"
import cn from "classnames"
import { ControllerRenderProps } from "react-hook-form"
import { useTranslation } from "react-i18next"

import { colors } from "shared/config"
import { FontsIcon, JsonIcon, ListIcon } from "shared/ui/icons"

const { TextArea } = Input

interface AttributFormProps {
  errors?: Record<string, string>
  index?: number
  fieldProps:
    | ControllerRenderProps<ResultFormData, "attributes">
    | ControllerRenderProps<TestCaseFormData, "attributes">
  attribut: Attribute
  handleAttributeRemove: (attributeId: string) => void
  handleAttributeChangeName: (attributeId: string, name: string) => void
  handleAttributeChangeValue: (attributeId: string, value: string) => void
  handleAttributeChangeType: (attributeId: string, type: AttributeType) => void
}

export const AttributForm = ({
  errors,
  index,
  fieldProps,
  attribut,
  handleAttributeRemove,
  handleAttributeChangeName,
  handleAttributeChangeValue,
  handleAttributeChangeType,
}: AttributFormProps) => {
  const { t } = useTranslation()

  return (
    <>
      <div id={`attribute-block-${index}`}>
        <Flex wrap style={{ paddingBottom: 8, rowGap: 8, columnGap: 16 }}>
          <Col flex="auto">
            <Input
              id={`attribute-name-${index}`}
              value={attribut.name}
              onChange={(e) => handleAttributeChangeName(attribut.id, e.target.value)}
              onBlur={fieldProps.onBlur}
              style={{ borderColor: errors?.name ? colors.error : "" }}
            />
          </Col>
          <Col style={{ textAlign: "right" }}>
            <Radio.Group
              value={attribut.type}
              onChange={(e) =>
                handleAttributeChangeType(attribut.id, e.target.value as AttributeType)
              }
            >
              <Tooltip placement="topRight" title={t("Text value")}>
                <Radio.Button id={`attribute-type-text-${index}`} value="Text">
                  <FontsIcon />
                </Radio.Button>
              </Tooltip>
              <Tooltip placement="topRight" title={t("List value")}>
                <Radio.Button id={`attribute-type-list-${index}`} value="List">
                  <ListIcon />
                </Radio.Button>
              </Tooltip>
              <Tooltip placement="topRight" title={t("JSON value")}>
                <Radio.Button id={`attribute-type-json-${index}`} value="JSON">
                  <JsonIcon />
                </Radio.Button>
              </Tooltip>
            </Radio.Group>
          </Col>
        </Flex>

        <TextArea
          id={`attribute-value-${index}`}
          className={cn({ [`attribute-value-${index}-req`]: !!attribut.required })}
          rows={4}
          value={String(attribut.value)}
          onChange={(e) => handleAttributeChangeValue(attribut.id, e.target.value)}
          onBlur={fieldProps.onBlur}
          style={{ borderColor: errors?.value ? colors.error : "" }}
        />

        <div style={{ textAlign: "right" }}>
          {!attribut.required ? (
            <Button
              id={`delete-attribute-${index}`}
              style={{ padding: 0, fontSize: "12px", height: "20px" }}
              type="link"
              danger
              onClick={() => {
                handleAttributeRemove(attribut.id)
              }}
            >
              {t("Delete attribute")}
            </Button>
          ) : (
            <Typography.Text type="secondary">*required</Typography.Text>
          )}
        </div>
      </div>

      <Divider type={"horizontal"} style={{ width: "100%", margin: "0 0 8px 0" }} dashed />
    </>
  )
}
