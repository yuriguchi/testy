import { useEffect } from "react"

import { icons } from "shared/assets/inner-icons"
import { useCacheState } from "shared/hooks"
import { toBool } from "shared/libs"

import { ContainerLoader } from "../container-loader"
import styles from "./styles.module.css"

const { ArrowIcon } = icons

interface Props extends HTMLDataAttribute {
  children: React.ReactNode
  cacheKey: string
  collapse?: boolean
  defaultCollapse?: boolean
  title: React.ReactNode
  isLoading?: boolean
  onOpenChange?: (toggle: boolean) => void
}

export const Collapse = ({
  children,
  cacheKey,
  collapse,
  defaultCollapse = false,
  title,
  isLoading = false,
  onOpenChange,
  ...props
}: Props) => {
  const [value, update] = useCacheState(`collapse-${cacheKey}`, Boolean(defaultCollapse), toBool)

  const handleOpen = () => {
    if (onOpenChange) {
      onOpenChange(!value)
    }
    update(!value)
  }

  useEffect(() => {
    if (collapse === undefined) return
    update(collapse)
  }, [collapse])

  return (
    <div className={styles.collapseBlock} {...props}>
      <div className={styles.collapseBlockTitle} onClick={handleOpen}>
        <ArrowIcon
          width={24}
          height={24}
          style={{ transform: `rotate(${value ? 270 : 360}deg)` }}
        />
        {title}
      </div>
      {!value && !isLoading && children}
      {isLoading && !value && <ContainerLoader />}
    </div>
  )
}
