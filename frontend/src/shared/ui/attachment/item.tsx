import { CloseOutlined, CopyOutlined, FileOutlined } from "@ant-design/icons"
import { Col, Row, Space, message } from "antd"

interface AttachmentItemProps {
  attachment: IAttachment
  handleAttachmentRemove?: (fileId: number) => void
}

export const AttachmentItem = ({ attachment, handleAttachmentRemove }: AttachmentItemProps) => {
  return (
    <Row style={{ border: "1px solid #ddd", marginBottom: 8 }} align="middle">
      <Col flex="0 1 60px" style={{ padding: "16px 16px" }}>
        <FileOutlined style={{ color: "#096dd9", fontSize: 32 }} />
      </Col>

      <Col
        flex="1 1"
        style={{
          textOverflow: "ellipsis",
          overflow: "hidden",
          whiteSpace: "nowrap",
        }}
        data-testid={`attachment-name-${attachment.name}`}
      >
        {attachment.name}
      </Col>

      <Col flex="0 1 100px" style={{ textAlign: "center" }}>
        <Space>
          <CopyOutlined
            onClick={() => {
              navigator.clipboard.writeText(attachment.link)
              message.info("Attachment url copied to clipboard")
            }}
            style={{ fontSize: 16, cursor: "pointer", color: "#ааа" }}
            data-testid={`attachment-copy-btn-${attachment.name}`}
          />
          {handleAttachmentRemove && (
            <CloseOutlined
              data-testid={`attachment-remove-btn-${attachment.name}`}
              onClick={() => handleAttachmentRemove(attachment.id)}
              style={{ fontSize: 16, cursor: "pointer", color: "#eb2f96" }}
            />
          )}
        </Space>
      </Col>
    </Row>
  )
}
