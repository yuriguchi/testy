import { Input } from "antd"
import { forwardRef, useEffect, useState } from "react"

import { MarkdownViewer, MarkdownViewerTabs } from ".."
import styles from "./styles.module.css"

type ViewTab = "md" | "view"

const { TextArea: TextAreaAntd } = Input

type CustomTextAreaProps = React.ComponentProps<typeof TextAreaAntd>

// eslint-disable-next-line react/display-name
export const TextArea: React.FC<CustomTextAreaProps> = forwardRef(
  ({ id = "text-area", ...props }, ref) => {
    const [tab, setTab] = useState<ViewTab>("md")
    const [textAreaHeight, setTextAreaHeight] = useState<number | null>(null)

    const handleTabClick = (newTab: ViewTab) => {
      setTab(newTab)
    }

    useEffect(() => {
      const el = document.querySelector(`#${id}`)

      function textAreaResize() {
        if (!el || el.clientHeight === 0) return
        setTextAreaHeight(el?.clientHeight ?? 0)
      }

      let resizeObserver: ResizeObserver
      if (el) {
        resizeObserver = new ResizeObserver(textAreaResize)
        resizeObserver.observe(el)
      }
      return () => resizeObserver?.disconnect()
    }, [id])

    return (
      <div id={`wrapper-${id}`}>
        <Input.TextArea
          id={id}
          rows={4}
          ref={ref}
          style={{
            fontSize: 13,
            borderBottomLeftRadius: 0,
            display: tab === "md" ? "inline-block" : "none",
            ...props.style,
          }}
          {...props}
        />
        <MarkdownViewer tab={tab} textAreaHeight={textAreaHeight} value={props.value as string} />
        <div id={`${id}-bottom`} className={styles.row}>
          <MarkdownViewerTabs id={id} tab={tab} handleTabClick={handleTabClick} />
        </div>
      </div>
    )
  }
)
