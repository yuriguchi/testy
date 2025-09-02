import { Switch, Table } from "antd"
import { ColumnsType } from "antd/es/table"
import {
  useDisableNotificationMutation,
  useEnableNotificationMutation,
  useGetNotificationSettingsQuery,
} from "entities/notifications/api"
import { useState } from "react"
import { useTranslation } from "react-i18next"

import { initInternalError } from "shared/libs"

export const NotificationSettingsTable = () => {
  const { t } = useTranslation()
  const { data, isFetching } = useGetNotificationSettingsQuery()
  const [enableSetting] = useEnableNotificationMutation()
  const [disableSetting] = useDisableNotificationMutation()
  const [isEnableLoading, setIsEnableLoading] = useState(false)

  const handleChangeSetting = async (action_code: number, enabled: boolean) => {
    const reqData = {
      settings: [action_code],
    }

    try {
      setIsEnableLoading(true)
      if (enabled) {
        await enableSetting(reqData)
      } else {
        await disableSetting(reqData)
      }
    } catch (e) {
      initInternalError(e)
    } finally {
      setIsEnableLoading(false)
    }
  }

  const columns: ColumnsType<NotificationSetting> = [
    {
      title: t("Name"),
      dataIndex: "verbose_name",
      key: "name",
    },
    {
      width: 100,
      title: t("Enabled"),
      dataIndex: "enabled",
      key: "enabled",
      render: (enabled: boolean, record) => {
        return (
          <Switch
            checked={enabled}
            onChange={(checked) => handleChangeSetting(record.action_code, checked)}
          />
        )
      },
    },
  ]

  return (
    <Table
      loading={isFetching || isEnableLoading}
      dataSource={data}
      columns={columns}
      rowKey="action_code"
      style={{ marginTop: 12 }}
      id="administration-projects-labels"
      rowClassName="administration-projects-labels-row"
      pagination={false}
    />
  )
}
