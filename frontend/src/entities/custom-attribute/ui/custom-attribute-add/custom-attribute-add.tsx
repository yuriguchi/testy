import { PlusOutlined } from "@ant-design/icons"
import { Button } from "antd"
import { useTranslation } from "react-i18next"

import styles from "./styles.module.css"

interface Props {
  onClick: () => void
}

export const CustomAttributeAdd = ({ onClick }: Props) => {
  const { t } = useTranslation()
  return (
    <Button id="add-attribute-btn" type="dashed" block onClick={onClick} className={styles.button}>
      <PlusOutlined /> {t("Add attribute")}
    </Button>
  )
}
