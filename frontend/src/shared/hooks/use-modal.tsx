import { useCallback, useEffect, useState } from "react"

const KEY_NAME_ESC = "Escape"
const KEY_EVENT_TYPE = "keyup"

export const useModal = (defaultToggle = false) => {
  const [isShow, setIsShow] = useState(defaultToggle)

  const handleClose = () => {
    setIsShow(false)
  }

  const handleShow = () => {
    setIsShow(true)
  }

  const handleEscKey = useCallback(
    (event: KeyboardEvent) => {
      if (event.key === KEY_NAME_ESC) {
        handleClose()
      }
    },
    [handleClose]
  )

  useEffect(() => {
    document.addEventListener(KEY_EVENT_TYPE, handleEscKey, false)

    return () => {
      document.removeEventListener(KEY_EVENT_TYPE, handleEscKey, false)
    }
  }, [handleEscKey])

  return {
    handleClose,
    handleShow,
    isShow,
  }
}
