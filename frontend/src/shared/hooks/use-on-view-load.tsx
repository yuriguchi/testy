import { useEffect, useState } from "react"
import { useInView } from "react-intersection-observer"
import { useParams } from "react-router-dom"

import { LazyGetTriggerType } from "app/export-types"

interface Params {
  page: number
  page_size: number
  search?: string
}

interface RequestParams extends Params {
  is_search?: boolean
}

interface UseOnViewLoadProps<T> {
  getData: LazyGetTriggerType<T>
  searchKey?: string
  dataParams?: Record<string, unknown>
  pageSize?: number
}

export const useOnViewLoad = <T extends BaseResponse>({
  getData,
  searchKey = "search",
  dataParams = {},
  pageSize = 10,
}: UseOnViewLoadProps<T>) => {
  const initParams: Params = {
    page: 1,
    page_size: pageSize,
    search: undefined,
  }
  // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-assignment
  const [activeRequest, setActiveRequest] = useState<any>(null)
  const { projectId } = useParams<ParamProjectId>()
  const [data, setData] = useState<T[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isLastPage, setIsLastPage] = useState(false)
  const [params, setParams] = useState<Params>(initParams)

  const { ref, inView } = useInView({
    threshold: 0,
    trackVisibility: true,
    delay: 100,
    skip: isLoading || isLastPage,
  })

  const fetchData = async ({ page, page_size, search, is_search }: RequestParams) => {
    if (activeRequest) {
      // eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-member-access
      activeRequest.abort()
    }

    let isFinished = false

    try {
      setIsLoading(true)
      const reqParams = {
        ...dataParams,
        page,
        page_size,
        project: projectId,
      }

      if (search) {
        //@ts-ignore
        reqParams[searchKey] = search
      }

      const res = getData(reqParams)
      setActiveRequest(res)
      const { data: resData } = await res
      if (!resData) {
        return
      }

      setData((prevState) => (!is_search ? [...prevState, ...resData.results] : resData.results))
      setIsLastPage(!resData.pages.next)

      isFinished = true
    } catch (err) {
      console.error(err)
    } finally {
      if (isFinished) {
        setIsLoading(false)
      }
    }
  }

  useEffect(() => {
    if (!inView || isLoading || isLastPage) return
    fetchData({
      page: params.page + 1,
      page_size: params.page_size,
      search: params.search,
    })
    setParams((prevState) => ({
      ...prevState,
      page: prevState.page + 1,
      page_size: prevState.page_size,
    }))
  }, [inView, isLoading, isLastPage])

  const reset = () => {
    setData([])
    setIsLoading(false)
    setIsLastPage(false)
    setParams(initParams)
  }

  const fetchInitData = () => {
    fetchData(params)
  }

  const handleSearchChange = (value: string) => {
    setData([])
    setParams({ page: 1, page_size: 10, search: value })
    setIsLastPage(false)
    fetchData({ page: 1, page_size: 10, search: value, is_search: true })
  }

  return {
    data,
    reset,
    fetchData,
    fetchInitData,
    handleSearchChange,
    isLastPage,
    isLoading,
    iref: ref,
  }
}
