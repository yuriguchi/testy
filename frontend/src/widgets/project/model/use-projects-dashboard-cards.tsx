import { MeContext } from "processes"
import { useContext, useEffect, useState } from "react"
import { useInView } from "react-intersection-observer"

import { useLazyGetProjectsQuery } from "entities/project/api"

interface RequestParams {
  page: number
  page_size: number
  is_archive?: boolean
  favorites?: boolean
  name?: string
}

export const useProjectsDashboardCards = ({ searchName }: { searchName: string }) => {
  const { userConfig } = useContext(MeContext)
  const [paginationParams, setPagingationParams] = useState({ page: 1, page_size: 10 })
  const [projects, setProjects] = useState<Project[]>([])
  const [isLastPage, setIsLastPage] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  const [getProjects] = useLazyGetProjectsQuery()
  // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-assignment
  const [activeRequest, setActiveRequest] = useState<any>(null)

  const { ref, inView } = useInView({
    threshold: 0,
    trackVisibility: true,
    delay: 100,
    skip: isLoading || isLastPage,
  })

  const fetchData = async (params: RequestParams, isSearch = false) => {
    if (activeRequest) {
      // eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-member-access
      activeRequest.abort()
    }

    try {
      setIsLoading(true)
      const res = getProjects({ ...params, ordering: "is_private" })
      setActiveRequest(res)
      const { data } = await res
      if (!data) {
        return
      }
      setProjects((prevState) => (!isSearch ? [...prevState, ...data.results] : data.results))
      setIsLastPage(!data.pages.next)
    } catch (err) {
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    if (!inView || isLoading || isLastPage) return
    setPagingationParams((prevState) => {
      fetchData({
        page: prevState.page + 1,
        page_size: prevState.page_size,
        is_archive: userConfig?.projects?.is_show_archived,
        favorites: userConfig?.projects?.is_only_favorite ?? false,
        name: searchName,
      })

      return {
        page: prevState.page + 1,
        page_size: prevState.page_size,
      }
    })
  }, [inView, isLoading, isLastPage])

  useEffect(() => {
    setPagingationParams((prevState) => {
      handleClear()
      fetchData({
        page: 1,
        page_size: prevState.page_size,
        is_archive: userConfig?.projects?.is_show_archived,
        favorites: userConfig?.projects?.is_only_favorite ?? false,
        name: searchName,
      })

      return {
        page: 1,
        page_size: prevState.page_size,
      }
    })
  }, [userConfig?.projects?.is_only_favorite, userConfig?.projects?.is_show_archived])

  useEffect(() => {
    handleClear()
    fetchData(
      {
        page: 1,
        page_size: paginationParams.page_size,
        is_archive: userConfig?.projects?.is_show_archived,
        favorites: userConfig?.projects?.is_only_favorite ?? false,
        name: searchName,
      },
      true
    )
  }, [searchName])

  const handleClear = () => {
    setPagingationParams({ page: 1, page_size: paginationParams.page_size })
    setProjects([])
    setIsLastPage(false)
  }

  return {
    projects,
    isLoading,
    isLastPage,
    bottomRef: ref,
  }
}
