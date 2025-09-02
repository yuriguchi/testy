import { DeleteOutlined, EditOutlined, MenuOutlined } from "@ant-design/icons"
import { Button } from "antd"

import styles from "./styles.module.css"

interface StepProps {
  index: number
  step: Step
  actions?: {
    onClickEdit: (step: Step) => void
    onClickDelete: (id: string) => void
  }
}

export const Step = ({ index, actions, step }: StepProps) => {
  return (
    <li className={styles.item} key={step.id}>
      <div className={styles.icon}>{index + 1}</div>
      <p className={styles.content}>{step.name}</p>
      {actions && (
        <div className={styles.actions}>
          <Button
            id={`${step.name}-edit`}
            onClick={() => actions.onClickEdit(step)}
            shape="circle"
            icon={<EditOutlined />}
          />
          <Button
            id={`${step.name}-delete`}
            danger
            shape="circle"
            onClick={() => actions.onClickDelete(step.id)}
            icon={<DeleteOutlined />}
          />
          <Button
            id={`${step.name}-move`}
            className="handle"
            style={{ border: "0" }}
            icon={<MenuOutlined />}
          />
        </div>
      )}
    </li>
  )
}
