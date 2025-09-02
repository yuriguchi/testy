import { CloseOutlined, EditOutlined } from "@ant-design/icons"
import { Button, Tag } from "antd"
import React from "react"

import { colors } from "shared/config"

import styles from "./styles.module.css"

interface StatusProps {
  content: React.ReactNode
  color?: string
  onClick?: (status: StatusInForm) => void
  onDelete?: (status: StatusInForm) => void
  onEdit?: (status: StatusInForm) => void
}

export const Status = ({ content, color, onDelete, onClick, onEdit }: StatusProps) => {
  return (
    <Tag
      className={styles.status}
      color={color !== "line-through" ? color : colors.accent}
      style={{
        cursor: onClick ? "pointer" : "default",
        textDecoration: color === "line-through" ? "line-through" : undefined,
      }}
      onClick={onClick ? () => onClick({ name: String(content) }) : undefined}
    >
      {content}
      {onEdit && (
        <Button
          id="status-edit"
          className={styles.btn}
          icon={<EditOutlined style={{ fontSize: 14 }} />}
          shape="default"
          onClick={() => onEdit({ name: String(content) })}
        />
      )}
      {onDelete && (
        <Button
          id="status-delete"
          className={styles.btn}
          icon={<CloseOutlined style={{ fontSize: 14 }} />}
          shape="default"
          onClick={() => onDelete({ name: String(content) })}
        />
      )}
    </Tag>
  )
}
