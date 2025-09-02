import { Markdown } from ".."

interface Props {
  textAreaHeight: number | null
  tab: "md" | "view"
  value: string
}

export const MarkdownViewer = ({ tab, textAreaHeight, value }: Props) => {
  return (
    <div
      className="mdViewer"
      style={{
        display: tab === "view" ? "block" : "none",
        minHeight: textAreaHeight ? textAreaHeight + 1 : "auto",
      }}
    >
      <Markdown content={value} />
    </div>
  )
}
