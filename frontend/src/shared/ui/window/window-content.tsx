import {
  Children,
  DetailedReactHTMLElement,
  HTMLAttributes,
  ReactNode,
  cloneElement,
  isValidElement,
  useCallback,
  useLayoutEffect,
  useRef,
} from "react"
import { Rnd, RndDragCallback, RndResizeCallback } from "react-rnd"

import { useOnClickOutside } from "shared/hooks"

import { Portal } from "widgets/[ui]/portal"

import { ContainerLoader } from "../container-loader"
import styles from "./styles.module.css"
import { useWindowContext } from "./window"
import { WindowBar } from "./window-bar"

const getSize = (cssStyleDeclaration: CSSStyleDeclaration) => {
  if (cssStyleDeclaration.boxSizing === "border-box") {
    return {
      h: parseInt(cssStyleDeclaration.height, 10),
      w: parseInt(cssStyleDeclaration.width, 10),
    }
  }

  return {
    h:
      parseInt(cssStyleDeclaration.height, 10) +
      parseInt(cssStyleDeclaration.marginTop, 10) +
      parseInt(cssStyleDeclaration.marginBottom, 10),
    w:
      parseInt(cssStyleDeclaration.width, 10) +
      parseInt(cssStyleDeclaration.marginLeft, 10) +
      parseInt(cssStyleDeclaration.marginRight, 10),
  }
}

interface Props {
  children: ReactNode
}

const TRIGGER_NAME = "WindowContent"
export const WindowContent = ({ children }: Props) => {
  // eslint-disable-next-line @typescript-eslint/unbound-method
  const { hide, open, isLoading, size, pos, minSize, setPos, setSize, onOpenChange } =
    useWindowContext(TRIGGER_NAME)
  const refChild = useRef<HTMLDivElement>(null)
  const rndRef = useRef<Rnd>(null)

  // @ts-ignore
  useOnClickOutside(rndRef.current?.resizableElement, () => onOpenChange(false))

  const handleDragStop: RndDragCallback = useCallback(
    (e, newPosition) => {
      setPos({ x: newPosition.x, y: newPosition.y })
    },
    [setPos]
  )

  const handleResizeStop: RndResizeCallback = useCallback(
    (e, dir, ref, delta, position) => {
      setSize({ height: ref.style.height, width: ref.style.width })
      setPos({ x: position.x, y: position.y })
    },
    [setSize]
  )

  useLayoutEffect(() => {
    // @ts-ignore
    // eslint-disable-next-line @typescript-eslint/no-unsafe-argument, @typescript-eslint/no-unsafe-member-access
    if (!refChild?.current?.nativeElement || !open) {
      return
    }

    const containerSize = getSize(getComputedStyle(document.body))
    // @ts-ignore
    // eslint-disable-next-line @typescript-eslint/no-unsafe-argument, @typescript-eslint/no-unsafe-member-access
    const childSize = getSize(getComputedStyle(refChild.current.nativeElement))
    const x = Math.floor(containerSize.w / 2 - childSize.w / 2)
    const y = Math.floor(containerSize.h / 6)
    setPos({ x, y })
  }, [refChild, open])

  if (!open) {
    return null
  }

  return (
    <Portal id="window-root">
      <Rnd
        ref={rndRef}
        minWidth={minSize?.width}
        minHeight={minSize?.height}
        className={styles.windowBlock}
        size={{ height: size.height, width: size.width }}
        position={{ x: pos.x, y: pos.y }}
        onResizeStop={handleResizeStop}
        enableResizing={{
          left: true,
          right: true,
          top: !hide,
          bottom: !hide,
          bottomLeft: !hide,
          bottomRight: !hide,
          topLeft: !hide,
          topRight: !hide,
        }}
        onDragStop={handleDragStop}
        bounds="window"
      >
        <div className={styles.windowContent}>
          {Children.map(children, (child) => {
            if (!isValidElement(child)) return null

            if (child.type === WindowBar) {
              return cloneElement(child)
            }

            if (isLoading) {
              return <ContainerLoader />
            }

            if (!hide) {
              return cloneElement<
                DetailedReactHTMLElement<HTMLAttributes<HTMLElement>, HTMLElement>
              >(
                // @ts-ignore
                child,
                {
                  ref: refChild,
                  // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
                  className: `${styles.windowContentBlock} ${child.props?.className}`,
                }
              )
            }

            return null
          })}
        </div>
      </Rnd>
    </Portal>
  )
}
