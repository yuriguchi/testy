import CollapseFullIcon from "shared/assets/icons/arrows-in.svg?react"
import CornersOutIcon from "shared/assets/icons/corners-out.svg?react"
import { icons } from "shared/assets/inner-icons"

import styles from "./styles.module.css"

const { CloseIcon, CollapseIcon } = icons

interface Props {
  title: string
  hide: boolean
  expand: boolean
  onClose: () => void
  onHide: () => void
  onExpand: () => void
}

export const WindowDefaultBar = ({ title, expand, hide, onClose, onHide, onExpand }: Props) => {
  return (
    <div className={styles.defaultBar}>
      <span className={styles.barTitle}>{title}</span>
      <div className={styles.barBtns}>
        <button className={styles.barBtn} type="button" onClick={onHide}>
          <CollapseIcon
            width={18}
            height={18}
            style={{ transform: !hide ? "rotate(180deg)" : "none" }}
          />
        </button>
        <button className={styles.barBtn} type="button" onClick={onExpand}>
          {expand ? (
            <CollapseFullIcon width={18} height={18} />
          ) : (
            <CornersOutIcon width={18} height={18} />
          )}
        </button>
        <button className={styles.barBtn} type="button" onClick={onClose}>
          <CloseIcon width={24} height={24} />
        </button>
      </div>
    </div>
  )
}
