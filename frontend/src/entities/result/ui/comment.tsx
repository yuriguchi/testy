import { Divider } from "antd"
import { useTranslation } from "react-i18next"

import { Markdown } from "shared/ui"

interface Props {
  result: Result
}

export const TestResultComment = ({ result }: Props) => {
  const { t } = useTranslation()
  return (
    <>
      <Divider orientation="left" style={{ margin: 0, fontSize: 14 }}>
        {t("Comment")}
      </Divider>
      <div className="content markdown" id="test-result-comment">
        <Markdown content={result.comment ? result.comment : t("No Comment")} />
      </div>
    </>
  )
}
