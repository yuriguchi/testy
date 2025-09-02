import { FileOutlined } from "@ant-design/icons"
import { Col, Divider, Row } from "antd"

interface IAttachmentsFieldProps {
  attachments: IAttachment[]
  isDivider?: boolean
}

export const AttachmentField = ({ attachments, isDivider = true }: IAttachmentsFieldProps) => {
  return (
    <>
      {isDivider && (
        <Divider orientation="left" style={{ margin: 0, fontSize: 14 }}>
          Attachments
        </Divider>
      )}
      {attachments.map((attachment, index) => {
        return (
          <Row align="middle" key={attachment.id} id={`attachment-${index + 1}`}>
            <Col flex="0 1 40px" style={{ padding: 8 }}>
              <FileOutlined style={{ color: "#096dd9", fontSize: 32 }} />
            </Col>
            <Col
              flex="1 1"
              style={{
                textOverflow: "ellipsis",
                overflow: "hidden",
                whiteSpace: "nowrap",
              }}
            >
              <a target="blank" href={attachment.link} style={{ margin: 0, fontSize: 13 }}>
                {attachment.filename}
              </a>
              <p
                style={{
                  margin: 0,
                  fontSize: 12,
                  color: "#828282",
                }}
              >
                {attachment.size_humanize}
              </p>
            </Col>
          </Row>
        )
      })}
    </>
  )
}
