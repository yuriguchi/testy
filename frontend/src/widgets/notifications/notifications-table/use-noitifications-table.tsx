import { TablePaginationConfig, TableProps } from "antd"
import { ColumnsType } from "antd/es/table"
import { useLazyGetNotificationsListQuery, useMarkAsMutation } from "entities/notifications/api"
import { useEffect, useState } from "react"
import { useTranslation } from "react-i18next"
import { Link } from "react-router-dom"

import { initInternalError } from "shared/libs"

import styles from "./notifications-table.module.css"

const PLACEHOLDER_TEXT = "{{placeholder}}"

const convertToLinkText = (record: NotificationData["message"]) => {
  const { template, placeholder_link, placeholder_text } = record

  const strings = template.split(PLACEHOLDER_TEXT) as [string, string]
  const renderString = (str: string) => !!str.length && <p style={{ margin: 0 }}>{str}</p>
  return (
    <span className={styles.linkRow}>
      {renderString(strings[0])}
      <Link to={placeholder_link}>{placeholder_text}</Link>
      {renderString(strings[1])}
    </span>
  )
}

export const useNotificationsTable = () => {
  const { t } = useTranslation()
  const [isLoading, setIsLoading] = useState(false)
  const [data, setData] = useState<NotificationData[]>([])
  const [pagination, setPagination] = useState<TablePaginationConfig>({ current: 1, pageSize: 10 })
  const [getNotifications] = useLazyGetNotificationsListQuery()
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([])
  const [markAs] = useMarkAsMutation()

  const columns: ColumnsType<NotificationData> = [
    {
      title: t("ID"),
      dataIndex: "id",
      key: "id",
      width: "70px",
    },
    {
      title: t("Message"),
      dataIndex: "message",
      key: "message",
      render: (record: NotificationData["message"]) => {
        if (!record) {
          return null
        }
        return convertToLinkText(record)
      },
    },
    {
      title: t("Actor"),
      dataIndex: "actor",
      key: "actor",
    },
    {
      title: t("Time"),
      dataIndex: "timeago",
      key: "timeago",
    },
  ]

  const fetchData = async ({
    force = false,
    paginationData = pagination,
  }: {
    force?: boolean
    paginationData?: TablePaginationConfig
  }) => {
    setIsLoading(true)
    try {
      const response = await getNotifications(
        {
          page: paginationData.current,
          page_size: paginationData.pageSize,
          v: force ? Date.now() : undefined,
        },
        false
      )
      setData(response?.data?.results ?? [])
      setPagination({ ...paginationData, total: response?.data?.count })
    } catch (error) {
      initInternalError(error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchData({})
  }, [])

  const handleChange: TableProps<NotificationData>["onChange"] = (newPagination) => {
    fetchData({ paginationData: newPagination })
  }

  const handleSelectRows = (newSelectedRowKeys: React.Key[]) => {
    setSelectedRowKeys(newSelectedRowKeys)
  }

  const handleRead = async () => {
    try {
      await markAs({
        unread: false,
        notifications: selectedRowKeys.map((key) => Number(key)),
      })
      fetchData({ force: true })
      setSelectedRowKeys([])
    } catch (error) {
      initInternalError(error)
    }
  }

  const handleUnread = async () => {
    try {
      await markAs({
        unread: true,
        notifications: selectedRowKeys.map((key) => Number(key)),
      })
      fetchData({ force: true })
      setSelectedRowKeys([])
    } catch (error) {
      initInternalError(error)
    }
  }

  return {
    isLoading,
    data,
    pagination,
    columns,
    handleChange,
    handleSelectRows,
    handleRead,
    handleUnread,
    selectedRowKeys,
  }
}
