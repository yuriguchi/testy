import { Divider } from "antd"

import { colors } from "shared/config"

import { Label } from "../label"
import styles from "./styles.module.css"

interface LabelFieldProps {
  title: string
  labels: LabelInForm[]
}

export const LabelField = ({ title, labels }: LabelFieldProps) => {
  return (
    <>
      <Divider orientation="left" style={{ margin: 0 }} orientationMargin={0}>
        {title}
      </Divider>
      <ul className={styles.list} data-testid="labels-list">
        {labels.map((label) => (
          <li key={label.id}>
            <Label content={label.name} color={colors.accent} />
          </li>
        ))}
      </ul>
    </>
  )
}
