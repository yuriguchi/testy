import ReactMarkdown from "react-markdown"
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter"
import { oneLight } from "react-syntax-highlighter/dist/esm/styles/prism"
import remarkGfm from "remark-gfm"

import "./styles.css"

interface MarkdownProps extends HTMLDataAttribute {
  content: string
}

export const Markdown = ({ content, ...props }: MarkdownProps) => {
  return (
    <ReactMarkdown
      children={content}
      linkTarget="_blank"
      components={{
        img: ({ ...propsImg }) => (
          <a href={propsImg.src} target="blank">
            <img {...propsImg} />
          </a>
        ),
        code({ inline, className = "", children, ...propsCode }) {
          const match = /language-(\w+)/.exec(className)
          return !inline && match ? (
            <SyntaxHighlighter
              {...propsCode}
              children={String(children).replace(/\n$/, "")}
              style={oneLight}
              language={match[1]}
              PreTag="div"
            />
          ) : (
            <code {...propsCode} className={className}>
              {children}
            </code>
          )
        },
        p: ({ children }) => {
          return <p style={{ whiteSpace: "pre-wrap" }}>{children}</p>
        },
      }}
      remarkPlugins={[remarkGfm]}
      {...props}
    />
  )
}
