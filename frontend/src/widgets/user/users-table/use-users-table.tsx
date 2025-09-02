import { Space, TablePaginationConfig } from "antd"
import { ColumnsType, TableProps } from "antd/es/table"
import { FilterValue } from "antd/lib/table/interface"
import { useState } from "react"
import { useTranslation } from "react-i18next"

import { useAppSelector } from "app/hooks"

import { selectUser } from "entities/auth/model"

import { useGetUsersQuery } from "entities/user/api"
import { UserAvatar } from "entities/user/ui/user-avatar/user-avatar"

import { DeleteUser, EditUser } from "features/user"

import { config } from "shared/config"
import { useTableSearch } from "shared/hooks"
import { CheckedIcon } from "shared/ui/icons"

export const useUsersTable = () => {
  const { t } = useTranslation()
  const [paginationParams, setPaginationParams] = useState({
    page: 1,
    page_size: 10,
  })
  const [filteredInfo, setFilteredInfo] = useState<Record<string, FilterValue | null>>({})
  const [filterInfoRequest, setFilteredInfoRequest] = useState<GetUsersQuery>({})
  const user = useAppSelector(selectUser)

  const { data: users, isLoading } = useGetUsersQuery({
    ...paginationParams,
    ...filterInfoRequest,
  })

  const { setSearchText, getColumnSearch } = useTableSearch()

  const handleChange: TableProps<User>["onChange"] = (
    pagination: TablePaginationConfig,
    filters: Record<string, FilterValue | null>
  ) => {
    setFilteredInfo(filters)
    setFilteredInfoRequest((prevState) => ({
      ...prevState,
      username: filters?.username ? String(filters.username[0]) : undefined,
      email: filters?.email ? String(filters.email[0]) : undefined,
      first_name: filters?.first_name ? String(filters.first_name[0]) : undefined,
      last_name: filters?.last_name ? String(filters.last_name[0]) : undefined,
      is_active: filters?.is_active ? Boolean(filters.is_active[0]) : undefined,
      is_superuser: filters?.is_superuser ? Boolean(filters.is_superuser[0]) : undefined,
    }))
  }

  const clearAll = () => {
    setFilteredInfo({})
    setFilteredInfoRequest({})
    setSearchText("")
  }

  const columns: ColumnsType<User> = [
    {
      key: "avatar",
      width: "32px",
      align: "right",
      render: (_, record) => <UserAvatar avatar_link={record.avatar_link} size={32} />,
    },
    {
      title: t("Username"),
      dataIndex: "username",
      key: "username",
      filteredValue: filteredInfo.username ?? null,
      ...getColumnSearch("username"),
      onFilter: (value, record) =>
        record.username.toLowerCase().includes(String(value).toLowerCase()),
    },
    {
      title: t("Email"),
      dataIndex: "email",
      key: "email",
      filteredValue: filteredInfo.email ?? null,
      ...getColumnSearch("email"),
      onFilter: (value, record) => record.email.toLowerCase().includes(String(value).toLowerCase()),
    },
    {
      title: t("First Name"),
      dataIndex: "first_name",
      key: "first_name",
      filteredValue: filteredInfo.first_name ?? null,
      ...getColumnSearch("first_name"),
      onFilter: (value, record) =>
        record.first_name.toLowerCase().includes(String(value).toLowerCase()),
    },
    {
      title: t("Last Name"),
      dataIndex: "last_name",
      key: "last_name",
      filteredValue: filteredInfo.last_name ?? null,
      ...getColumnSearch("last_name"),
      onFilter: (value, record) =>
        record.last_name.toLowerCase().includes(String(value).toLowerCase()),
    },
    {
      title: t("Active"),
      dataIndex: "is_active",
      key: "is_active",
      width: 100,
      filters: [
        {
          text: "Active",
          value: true,
        },
      ],
      filteredValue: filteredInfo.is_active ?? null,
      onFilter: (_, record) => record.is_active,
      render: (is_active: boolean) => <CheckedIcon value={is_active} />,
    },
    {
      title: t("Admin"),
      dataIndex: "is_superuser",
      key: "is_superuser",
      width: 100,
      filters: [
        {
          text: "Admin",
          value: true,
        },
      ],
      filteredValue: filteredInfo.is_superuser ?? null,
      onFilter: (_, record) => record.is_superuser,
      render: (is_superuser: boolean) => <CheckedIcon value={is_superuser} />,
    },
    {
      key: "action",
      width: 110,
      render: (_, record) => {
        return user?.is_superuser ? (
          <Space>
            <EditUser user={record} />
            <DeleteUser user={record} />
          </Space>
        ) : null
      },
    },
  ]

  const handlePaginationChange = (page: number, page_size: number) => {
    setPaginationParams({
      page,
      page_size,
    })
  }

  const paginationTable: TablePaginationConfig = {
    total: users?.pages.total ?? 0,
    hideOnSinglePage: false,
    pageSizeOptions: config.pageSizeOptions,
    showLessItems: true,
    showSizeChanger: true,
    current: paginationParams.page,
    pageSize: paginationParams.page_size,
    onChange: handlePaginationChange,
  }

  return {
    users: users?.results ?? [],
    isLoading,
    columns,
    paginationTable,
    handleChange,
    clearAll,
  }
}
