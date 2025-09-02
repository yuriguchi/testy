import { useTranslation } from "react-i18next"

interface Props {
  link?: string
  title: string
  id: string
  action: "updated" | "created" | "deleted" | "archived" | "added" | "copied" | "restore"
}

export const AlertSuccessChange = ({ action, id, link, title }: Props) => {
  const { t } = useTranslation()
  return (
    <span>
      {title} {link ? <a href={link}>{id}</a> : id} {t(action)} {t("successfully")}
    </span>
  )
}
