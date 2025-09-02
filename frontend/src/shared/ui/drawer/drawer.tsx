import { Col, Flex } from "antd"
import classNames from "classnames"
import { ReactNode, useRef } from "react"

import SquareHalfIcon from "shared/assets/icons/square-half.svg?react"
import { icons } from "shared/assets/inner-icons"
import { useCacheState, useOnClickOutside, useResizebleBlock } from "shared/hooks"
import { toBool } from "shared/libs"

import { Portal } from "widgets/[ui]/portal"

import { ContainerLoader } from "../container-loader"
import { ResizeLine } from "../resize-line/resize-line"
import styles from "./styles.module.css"

const { CloseIcon } = icons

interface Props {
  id: string
  isOpen: boolean
  onClose: () => void
  isLoading?: boolean
  title?: ReactNode
  extra?: ReactNode
  children?: ReactNode
  baseWidth?: number
  minWidth?: number
}

const MAX_WITH_PERCENT = 70
const INGNORED_LIST_OUTSIDE_CLICK = [
  ".ant-modal-root",
  ".ant-popover-content",
  ".anticon-close-circle",
  ".ant-notification-notice-wrapper",
  ".ant-select-dropdown",
  ".ant-dropdown",
  ".ant-picker-dropdown",
]

export const Drawer = ({
  id,
  isOpen,
  isLoading = false,
  minWidth = 500,
  baseWidth = minWidth,
  onClose,
  title,
  extra,
  children,
}: Props) => {
  const [isRightFixed, setIsRightFixed] = useCacheState(`isDrawerRightFixed`, false, toBool)

  const handleRightSide = () => {
    setIsRightFixed(!isRightFixed)
  }

  const drawerRef = useRef<HTMLDivElement>(null)
  const { width, handleMouseDown } = useResizebleBlock({
    key: id,
    elRef: drawerRef,
    defaultWidth: baseWidth,
    minWidth: minWidth,
    maxWidth: MAX_WITH_PERCENT,
    maxAsPercent: true,
    direction: "left",
  })
  useOnClickOutside(drawerRef, onClose, isOpen && !isRightFixed, INGNORED_LIST_OUTSIDE_CLICK)

  return (
    <Portal id="portal-root">
      <div
        id={id}
        ref={drawerRef}
        style={{ width }}
        className={classNames(styles.wrapper, {
          [styles.isOpen]: isOpen,
          [styles.fixedRight]: isRightFixed,
        })}
      >
        <ResizeLine onMouseDown={handleMouseDown} direction="left" />
        {isLoading && (
          <div className={styles.loaderBlock}>
            <ContainerLoader />
          </div>
        )}
        {!isLoading && (
          <>
            <Flex gap={16} justify="space-between" className={styles.header}>
              <Flex gap={4} style={{ minWidth: 68 }}>
                <Col flex="32px" style={{ padding: 0, height: 32 }}>
                  <CloseIcon
                    className={styles.closeIcon}
                    onClick={onClose}
                    id="drawer-close-icon"
                  />
                </Col>
                <Col flex="32px" style={{ padding: 0, height: 32 }}>
                  <SquareHalfIcon
                    className={classNames(styles.closeIcon, { [styles.iconActive]: isRightFixed })}
                    onClick={handleRightSide}
                    id="drawer-square-half-icon"
                  />
                </Col>
              </Flex>
              <Flex align="flex-start" style={{ width: "fit-content", marginRight: "auto" }}>
                {title}
              </Flex>
              {extra}
            </Flex>
            <div className={styles.body}>{children}</div>
          </>
        )}
      </div>
    </Portal>
  )
}
