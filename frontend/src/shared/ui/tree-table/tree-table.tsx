import { HTMLAttributes, ReactNode } from "react"
import { useTranslation } from "react-i18next"

import styles from "./styles.module.css"

interface Props extends HTMLAttributes<HTMLDivElement> {
  children?: ReactNode
  visibleColumns: ColumnParam[]
}

export const TreeTable = ({ children, visibleColumns }: Props) => {
  const { t } = useTranslation()

  return (
    <div className={styles.tableWrapper}>
      <table className={styles.table}>
        <thead className={styles.tableHead}>
          <tr>
            {visibleColumns.map((col) => (
              // @ts-ignore
              <th key={col.key}>{t(col.title)}</th>
            ))}
          </tr>
        </thead>
        <tbody className={styles.tableBody}>{children}</tbody>
      </table>
    </div>
  )
}
