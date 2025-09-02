import classNames from "classnames"
import { useEffect, useState } from "react"

import { icons } from "shared/assets/inner-icons"

import styles from "./styles.module.css"

const { ArrowIcon } = icons

export const BtnToTop = () => {
  const [isShow, setIsShow] = useState(false)

  const handleVisibleButton = () => {
    setIsShow(window.pageYOffset > 500)
  }

  const handleScrollUp = () => {
    window.scrollTo({ left: 0, top: 0, behavior: "smooth" })
  }

  useEffect(() => {
    window.addEventListener("scroll", handleVisibleButton)

    return () => {
      window.removeEventListener("scroll", handleVisibleButton)
    }
  }, [])

  return (
    <button
      type="button"
      className={classNames(styles.btn, { [styles.hide]: !isShow })}
      onClick={handleScrollUp}
    >
      <ArrowIcon style={{ transform: "rotate(180deg)" }} />
    </button>
  )
}
