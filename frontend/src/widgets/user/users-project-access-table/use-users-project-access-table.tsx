import { Space, TablePaginationConfig } from "antd"
import { ColumnsType, TableProps } from "antd/es/table"
import { FilterValue } from "antd/lib/table/interface"
import { resetOnSuccess, setOnSuccess } from "entities/roles/model"
import { useEffect, useState } from "react"
import { useTranslation } from "react-i18next"
import { useParams } from "react-router-dom"

import { useAppDispatch } from "app/hooks"

import { useGetMembersQuery } from "entities/project/api"

import { UserAvatar } from "entities/user/ui/user-avatar/user-avatar"

import { config } from "shared/config"
import { useTableSearch } from "shared/hooks"

import { DeleteUsetProjectAccess } from "../user-project-access-modal/delete-user-project-access"
import { EditUserProjectAccess } from "../user-project-access-modal/edit-user-project-access"

export const useUsersProjectAccessTable = (isManageable: boolean) => {
  const { t } = useTranslation()
  const dispatch = useAppDispatch()
  const [paginationParams, setPaginationParams] = useState({
    page: 1,
    page_size: 10,
  })
  const [filteredInfo, setFilteredInfo] = useState<Record<string, FilterValue | null>>({})
  const [filterInfoRequest, setFilteredInfoRequest] = useState<GetUsersQuery>({})
  const { projectId } = useParams<ParamProjectId>()

  const {
    data: users,
    isLoading,
    refetch,
  } = useGetMembersQuery({
    ...paginationParams,
    ...filterInfoRequest,
    id: Number(projectId),
  })

  const handleRefetch = async () => {
    await refetch()
    return
  }

  useEffect(() => {
    Promise.resolve(dispatch(setOnSuccess(handleRefetch)))

    return () => {
      dispatch(resetOnSuccess())
    }
  }, [dispatch, refetch])

  const { setSearchText, getColumnSearch } = useTableSearch()

  const handleChange: TableProps<UserWithRoles>["onChange"] = (
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
    }))
  }

  const clearAll = () => {
    setFilteredInfo({})
    setFilteredInfoRequest({})
    setSearchText("")
  }

  const columns: ColumnsType<UserWithRoles> = [
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
      title: t("Roles"),
      key: "roles",
      render: (_, record) => {
        if (record.roles.length === 0) {
          return "-"
        }
        return record.roles.map((role) => role.name).join(", ")
      },
    },
    {
      title: t("Actions"),
      key: "action",
      width: 110,
      render: (_, record) => (
        <Space>
          {isManageable && <EditUserProjectAccess user={record} />}
          {isManageable && <DeleteUsetProjectAccess user={record} />}
        </Space>
      ),
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
