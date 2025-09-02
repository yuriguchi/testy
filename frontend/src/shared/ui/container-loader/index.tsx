import { Spin } from "antd"
import React from "react"

import styles from "./styles.module.css"

export const ContainerLoader: React.FC = () => {
  return (
    <div className={styles.loader}>
      <Spin />
    </div>
  )
}
