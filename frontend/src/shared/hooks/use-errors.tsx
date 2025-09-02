import { Dispatch, SetStateAction } from "react"

import { initInternalError, isFetchBaseQueryError } from "shared/libs"

// prettier-ignore
export const useErrors = <T, >(onSetErrors: Dispatch<SetStateAction<T | null>>) => {
  const onHandleError = (err: unknown) => {
    if (isFetchBaseQueryError(err)) {
      if (err?.status && (err.status === 400 || err.status === 403)) {
        let errData = err.data as T
        if (err.status === 403) {
          errData = { errors: [(err.data as { detail: string })?.detail] } as T
        }
        onSetErrors(errData)
      } else {
        initInternalError(err)
      }
    } else {
      initInternalError(err)
    }
  }

  return {
    onHandleError,
  }
}
