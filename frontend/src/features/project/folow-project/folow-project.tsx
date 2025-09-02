import { Tooltip, notification } from "antd"
import { MeContext } from "processes"
import { useContext } from "react"
import { useTranslation } from "react-i18next"

import { icons } from "shared/assets/inner-icons"

import styles from "./styles.module.css"

const { BookmarkIcon, BookmarkFillIcon } = icons

export const FolowProject = ({ project }: { project: Project }) => {
  const { t } = useTranslation()
  const { userConfig, updateConfig } = useContext(MeContext)

  const handleFavoriteClick = async (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (!project.is_visible) {
      return
    }
    const isNew = !userConfig?.projects?.favorite.some((i) => i === project.id)

    const newProjectIds = isNew
      ? userConfig?.projects?.favorite.concat([project.id])
      : userConfig?.projects?.favorite.filter((i) => Number(i) !== Number(project.id))

    const newConfig = {
      ...userConfig,
      projects: {
        ...userConfig?.projects,
        favorite: newProjectIds,
      },
    }

    try {
      await updateConfig(newConfig)

      notification.success({
        message: t("Success"),
        closable: true,
        description: `${project.name} ${isNew ? t("has been added to favorites") : t("has been removed to favorites")}`,
      })
    } catch (error) {
      notification.error({
        message: t("Error!"),
        closable: true,
        description: t("Error when try to change follow project"),
      })
      console.error(error)
    }
  }

  const isFavoriteActive = !!userConfig?.projects?.favorite?.some((i) => i === project.id)

  return (
    <Tooltip title={t("Add to favorites")}>
      <div
        id={`${project.name}-project-favorite-btn`}
        data-test-active={isFavoriteActive}
        className={styles.icon}
        onClick={handleFavoriteClick}
      >
        {!isFavoriteActive ? <BookmarkIcon /> : <BookmarkFillIcon />}
      </div>
    </Tooltip>
  )
}
