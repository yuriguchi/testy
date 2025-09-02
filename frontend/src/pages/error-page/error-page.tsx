import { Button, Result } from "antd"
import { ResultStatusType } from "antd/es/result"
import { Link } from "react-router-dom"

import styles from "./styles.module.css"

interface Props {
  code: ResultStatusType
  message: string
}

export const ErrorPage = ({ code, message }: Props) => {
  return (
    <div className={styles.wrapper}>
      <Result
        status={code}
        title={code}
        subTitle={message}
        extra={
          <Button type="primary">
            <Link to="/">Back to Home</Link>
          </Button>
        }
      />
    </div>
  )
}
