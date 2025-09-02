import { Select, Spin } from "antd"
import { MeContext } from "processes"
import { useContext, useEffect, useState } from "react"
import { useTranslation } from "react-i18next"
import { useInView } from "react-intersection-observer"

import { useLazyGetUserByIdQuery, useLazyGetUsersQuery } from "entities/user/api"

import { NOT_ASSIGNED_FILTER_VALUE } from "shared/constants"

import { UserSearchOption } from "../user-search-option"

interface Props {
  value?: string[]
  onChange: (value?: string[]) => void
  onClear: () => void
  placeholder?: string
  project?: Project
  onClose?: () => void
}

export const AssigneeFilter = ({
  value,
  placeholder,
  project,
  onChange,
  onClear,
  onClose,
}: Props) => {
  const { t } = useTranslation()
  const { me } = useContext(MeContext)

  const [search, setSearch] = useState<string>("")
  const [searchUsers, setSearchUsers] = useState<User[]>([])
  const [selectedUsers, setSelectedUsers] = useState<User[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingMore, setIsLoadingMore] = useState(false)
  const [isLoadingInitUsers, setIsLoadingInitUsers] = useState(false)

  const [getUsers] = useLazyGetUsersQuery()
  const [getUserById] = useLazyGetUserByIdQuery()
  const [isLastPage, setIsLastPage] = useState(false)
  const [isOpen, setIsOpen] = useState(false)

  const { ref, inView } = useInView()
  const [currentPage, setCurrentPage] = useState(1)

  const filterUsersSearch = (result: User[]) => {
    const selectedIds = new Set(selectedUsers.map((user) => user.id))
    return result.filter((user) => !selectedIds.has(user.id) && user.id !== me?.id)
  }

  const handleSearch = async (newValue: string) => {
    if (!newValue.length) {
      setSearchUsers([])
      setSearch("")
      setIsLastPage(false)
      return
    }

    const additionalFilter = project
      ? { [project.is_private ? "project" : "exclude_external"]: project.id }
      : {}

    setIsLoading(true)
    const res = await getUsers({
      page: 1,
      page_size: 10,
      username: newValue,
      ...additionalFilter,
    }).unwrap()

    if (!res.pages.next) {
      setIsLastPage(true)
    }

    setSearchUsers(filterUsersSearch(res.results))
    setSearch(newValue)
    setIsLoading(false)
  }

  const handleChange = (dataValue: string[]) => {
    if (!dataValue.length) {
      onClear()
      return
    }

    onChange(dataValue)
  }

  const handleDropdownVisibleChange = (toggle: boolean) => {
    setIsOpen(toggle)
    if (!toggle) {
      onClose?.()
    }
  }

  useEffect(() => {
    if (!inView || !search.length || isLastPage || isLoading) return

    const fetch = async () => {
      setIsLoadingMore(true)
      const res = await getUsers({
        page: currentPage + 1,
        page_size: 10,
        username: search,
      }).unwrap()

      if (!res.pages.next) {
        setIsLastPage(true)
      }

      const filteredResults = filterUsersSearch(res.results)
      setSearchUsers((prevState) => [...prevState, ...filteredResults])
      if (res.pages.current < res.pages.total) {
        setCurrentPage((prev) => prev + 1)
      }
      setIsLoadingMore(false)
    }

    fetch()
  }, [inView, search, isLastPage, isLoading])

  useEffect(() => {
    if (!value?.length || isLoadingInitUsers || selectedUsers.length) {
      return
    }

    const assignedUserIdsFromFilter = value.filter(
      (i) => i !== String(me?.id) && i !== "null" && i.length
    )

    const fetchUsers = async () => {
      setIsLoadingInitUsers(true)
      const loadedUsers: User[] = []
      for (const needLoadUserId of assignedUserIdsFromFilter) {
        const loadedUser = await getUserById(Number(needLoadUserId)).unwrap()
        loadedUsers.push(loadedUser)
      }
      setSelectedUsers(loadedUsers)
      setIsLastPage(true)
      setIsLoadingInitUsers(false)
    }
    fetchUsers()
  }, [value, isLoadingInitUsers, me])

  useEffect(() => {
    const valueIdsSet = new Set(selectedUsers.map((user) => user.id))
    const searchUsersFiltered = searchUsers.filter((user) => !valueIdsSet.has(user.id))
    setSearchUsers(searchUsersFiltered)
  }, [selectedUsers])

  return (
    <Select
      id="assignee-filter"
      value={value ?? []}
      mode="multiple"
      showSearch
      loading={isLoadingInitUsers || isLoading}
      placeholder={placeholder ?? t("Search a user")}
      defaultActiveFirstOption={false}
      showArrow
      filterOption={false}
      onSearch={handleSearch}
      onChange={handleChange}
      onClear={onClear}
      open={isOpen}
      onDropdownVisibleChange={handleDropdownVisibleChange}
      notFoundContent={t("No matches")}
      allowClear
      style={{ width: "100%" }}
    >
      <Select.Option value={NOT_ASSIGNED_FILTER_VALUE} data-testid="assignee-filter-not-assigned">
        {t("Not Assigned")}
      </Select.Option>
      {me && (
        <Select.Option value={String(me.id)} data-testid="assignee-filter-me">
          <UserSearchOption user={me} />
        </Select.Option>
      )}
      {!isLoadingInitUsers &&
        selectedUsers.map((user) => (
          <Select.Option
            key={user.id}
            value={String(user.id)}
            data-testid={`assignee-filter-user-${user.username}`}
          >
            <UserSearchOption user={user} />
          </Select.Option>
        ))}
      {!isLoading &&
        searchUsers.map((user) => (
          <Select.Option
            key={user.id}
            value={String(user.id)}
            data-testid={`assignee-filter-user-${user.username}`}
          >
            <UserSearchOption user={user} />
          </Select.Option>
        ))}
      {!!searchUsers.length && !isLastPage && !isLoadingMore && (
        <Select.Option value="">
          <div ref={ref} />
        </Select.Option>
      )}
      {isLoadingMore && (
        <Select.Option value="">
          <div style={{ display: "flex", justifyContent: "center", alignItems: "center" }}>
            <Spin />
          </div>
        </Select.Option>
      )}
    </Select>
  )
}
