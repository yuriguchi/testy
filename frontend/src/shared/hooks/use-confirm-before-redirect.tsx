import { useEffect, useRef } from "react"
import { useBlocker } from "react-router-dom"

interface Props {
  isDirty: boolean
  pathname: string
}

export const useConfirmBeforeRedirect = ({ isDirty, pathname }: Props) => {
  const redirectByUser = useRef(false)

  useEffect(() => {
    //@ts-ignore
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const onBeforeUnload = (e: any) => {
      if (isDirty) {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access, @typescript-eslint/no-unsafe-call
        e.preventDefault()
        // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
        e.returnValue = ""
      }
    }

    window.addEventListener("beforeunload", onBeforeUnload)

    return () => {
      window.removeEventListener("beforeunload", onBeforeUnload)
    }
  }, [isDirty])

  useBlocker(({ currentLocation, nextLocation }) => {
    if (
      isDirty &&
      currentLocation.pathname.includes(pathname) &&
      currentLocation.pathname !== nextLocation.pathname &&
      !redirectByUser.current
    ) {
      const isConfirmed = confirm("Are you sure? All changes will be lost.")
      return !isConfirmed
    }
    return false
  })

  const setIsRedirectByUser = () => {
    redirectByUser.current = true
  }

  return {
    setIsRedirectByUser,
  }
}
