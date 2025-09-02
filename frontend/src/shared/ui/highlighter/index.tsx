import Highlighter from "react-highlight-words"

import { colors } from "shared/config"

interface HighLighterTestyProps {
  searchWords: string
  textToHighlight: string
  backgroundColor?: string
  color?: string
}

export const HighLighterTesty = ({
  searchWords,
  textToHighlight,
  backgroundColor = "#d9d9d9",
  color = colors.accent,
}: HighLighterTestyProps) => {
  return (
    <Highlighter
      autoEscape
      highlightStyle={{
        backgroundColor,
        color,
        padding: 0,
      }}
      searchWords={[searchWords]}
      textToHighlight={textToHighlight ?? ""}
    />
  )
}
