import { CloseOutlined, EditOutlined } from "@ant-design/icons"
import { Button, Tag } from "antd"

import { colors } from "shared/config"

import styles from "./styles.module.css"

interface LabelProps {
  content: string
  color?: string
  onClick?: (label: LabelInForm) => void
  onDelete?: (label: LabelInForm) => void
  onEdit?: (label: LabelInForm) => void
}

export const Label = ({ content, color, onDelete, onClick, onEdit }: LabelProps) => {
  return (
    <Tag
      className={styles.label}
      color={color !== "line-through" ? color : colors.accent}
      style={{
        cursor: onClick ? "pointer" : "default",
        textDecoration: color === "line-through" ? "line-through" : undefined,
      }}
      onClick={onClick ? () => onClick({ name: content }) : undefined}
      data-testid={`label-${content}`}
    >
      {content}
      {onEdit && (
        <Button
          id="label-edit"
          className={styles.btn}
          icon={<EditOutlined style={{ fontSize: 14 }} />}
          shape="default"
          onClick={() => onEdit({ name: content })}
          data-testid={`label-edit-${content}`}
        />
      )}
      {onDelete && (
        <Button
          id="label-delete"
          className={styles.btn}
          icon={<CloseOutlined style={{ fontSize: 14 }} />}
          shape="default"
          onClick={() => onDelete({ name: content })}
          data-testid={`label-delete-${content}`}
        />
      )}
    </Tag>
  )
}
