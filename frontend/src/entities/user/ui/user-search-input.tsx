import { Select, Spin } from "antd"
import { useEffect, useState } from "react"
import { useTranslation } from "react-i18next"
import { useInView } from "react-intersection-observer"

import { useLazyGetUsersQuery } from "../api"
import { UserSearchOption } from "./user-search-option"

interface Props {
  handleChange: (value?: SelectData) => void
  handleClear: () => void
  selectedUser?: SelectData | null
  placeholder?: string
  project?: Project
}

export const UserSearchInput = ({
  selectedUser,
  handleClear,
  handleChange: handleChangeUserSearchInput,
  placeholder,
  project,
}: Props) => {
  const { t } = useTranslation()
  const [search, setSearch] = useState<string>("")
  const [data, setData] = useState<User[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [getUsers, { data: dataGetTestSuites, isLoading: isLoadingGetTestSuites }] =
    useLazyGetUsersQuery()
  const [isLastPage, setIsLastPage] = useState(false)

  const { ref, inView } = useInView()
  const [currentPage, setCurrentPage] = useState(1)

  const handleSearch = async (newValue: string) => {
    if (!newValue.length) {
      setData([])
      setSearch("")
      setIsLastPage(false)
      return
    }

    setIsLoading(true)

    const additionalFilter = project
      ? { [project.is_private ? "project" : "exclude_external"]: project.id }
      : {}

    const res = await getUsers({
      page: 1,
      page_size: 10,
      username: newValue,
      ...additionalFilter,
    }).unwrap()

    if (!res.pages.next) {
      setIsLastPage(true)
    }

    setData(res.results)
    setSearch(newValue)
    setIsLoading(false)
  }

  const handleChange = (dataValue?: SelectData) => {
    if (!dataValue) {
      handleClear()
      return
    }

    handleChangeUserSearchInput(dataValue)
  }

  useEffect(() => {
    if (!inView || !search.length || isLastPage || isLoadingGetTestSuites) return

    const fetch = async () => {
      setIsLoading(true)

      const res = await getUsers({
        page: currentPage + 1,
        page_size: 10,
      }).unwrap()

      if (!res.pages.next) {
        setIsLastPage(true)
      }

      setData((prevState) => [...prevState, ...res.results])
      if (res.pages.current < res.pages.total) {
        setCurrentPage((prev) => prev + 1)
      }

      setIsLoading(false)
    }

    fetch()
  }, [inView, search, isLastPage, isLoadingGetTestSuites, dataGetTestSuites])

  return (
    <Select
      id="select-user"
      value={selectedUser}
      showSearch
      labelInValue
      placeholder={placeholder ?? t("Search a user")}
      defaultActiveFirstOption={false}
      showArrow
      filterOption={false}
      onSearch={handleSearch}
      onChange={handleChange}
      notFoundContent={t("No matches")}
      allowClear
      style={{ width: "100%" }}
    >
      {data.map((user) => (
        <Select.Option key={user.id} value={user.id}>
          <UserSearchOption user={user} />
        </Select.Option>
      ))}
      {!!data.length && !isLastPage && !isLoading && !isLoadingGetTestSuites && (
        <Select.Option value="">
          <div ref={ref} />
        </Select.Option>
      )}
      {isLoading && (
        <Select.Option value="">
          <div style={{ display: "flex", justifyContent: "center", alignItems: "center" }}>
            <Spin />
          </div>
        </Select.Option>
      )}
    </Select>
  )
}
