import { Badge, Tooltip } from "antd"
import cn from "classnames"
import classNames from "classnames"
import { useNotificationWS } from "entities/notifications/model/use-notification-ws"
import { memo } from "react"
import { useTranslation } from "react-i18next"
import { Link, useLocation, useNavigate, useParams } from "react-router-dom"

import { useAppSelector } from "app/hooks"

import { useLogoutMutation } from "entities/auth/api"
import { selectUser } from "entities/auth/model"

import NotificationIcon from "shared/assets/icons/bell.svg?react"
import TestyIcon from "shared/assets/icons/testy.svg?react"
import { icons } from "shared/assets/inner-icons"

import styles from "./styles.module.css"

const {
  ColumnViewIcon,
  DashboardIcon,
  LogoutIcon,
  TestPlansIcon,
  TestSuitesIcon,
  UserGroupsIcon,
  UserIcon,
} = icons

export const Sidebar = memo(() => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { projectId } = useParams<ParamProjectId>()
  const location = useLocation()
  const [logoutRequest] = useLogoutMutation()
  const user = useAppSelector(selectUser)
  const { notificationsCount } = useNotificationWS()

  const UP_LINKS = [
    {
      key: "overview",
      to: `/projects/${projectId}/overview`,
      title: t("Overview"),
      icon: <DashboardIcon className={styles.icon} />,
    },
    {
      key: "suites",
      to: `/projects/${projectId}/suites`,
      title: t("Test Suites & Cases"),
      icon: <TestSuitesIcon className={styles.icon} />,
    },
    {
      key: "plans",
      to: `/projects/${projectId}/plans`,
      title: t("Test Plans & Results"),
      icon: <TestPlansIcon className={styles.icon} />,
    },
  ]

  const MIDDLE_LINKS = [
    {
      key: "administration/projects",
      to: "/administration/projects",
      title: t("Projects"),
      icon: <ColumnViewIcon className={styles.icon} />,
      is_private: false,
    },
    {
      key: "administration/users",
      to: "/administration/users",
      title: t("Users"),
      icon: <UserGroupsIcon className={styles.icon} />,
      is_private: true,
    },
  ]

  const handleLogout = () => {
    logoutRequest()
      .unwrap()
      .then(() => {
        navigate("/login")
      })
  }

  return (
    <div className={styles.wrapper}>
      <Link id="logo" to="/">
        <TestyIcon />
      </Link>
      {location.pathname.includes("project") && !location.pathname.includes("administration") && (
        <ul className={styles.links}>
          {UP_LINKS.map((link) => (
            <Tooltip key={link.key} title={link.title} placement="right">
              <Link
                id={`sidebar-link-${link.key}`}
                to={link.to}
                className={cn(styles.link, {
                  [styles.active]: location.pathname.includes(`/${link.key}`),
                })}
              >
                {link.icon}
              </Link>
            </Tooltip>
          ))}
        </ul>
      )}
      <ul className={cn(styles.links, styles.linksBottom)}>
        <ul className={styles.links}>
          {MIDDLE_LINKS.map((link) => {
            if (link.is_private && !user?.is_superuser) return null

            return (
              <Tooltip key={link.key} title={link.title} placement="right">
                <Link
                  id={`sidebar-link-${link.key}`}
                  to={link.to}
                  className={cn(styles.link, {
                    [styles.active]: location.pathname.includes(link.to),
                  })}
                >
                  {link.icon}
                </Link>
              </Tooltip>
            )
          })}
        </ul>
        <Tooltip title={t("Notifications")} placement="right">
          <Link
            id="sidebar-link-notifications"
            to="/notifications"
            className={cn(styles.link, {
              [styles.active]: location.pathname.includes("/notifications"),
            })}
          >
            <NotificationIcon className={styles.icon} />
            <Badge
              className={classNames(styles.badge, { [styles.hide]: !notificationsCount })}
              color="var(--y-interactive-default)"
              count={notificationsCount}
              showZero={false}
            />
          </Link>
        </Tooltip>
        <div className={styles.divider} />
        <Tooltip title={t("Profile")} placement="right">
          <Link
            id="sidebar-link-profile"
            to="/profile"
            className={cn(styles.link, { [styles.active]: location.pathname === "/profile" })}
          >
            <UserIcon className={styles.icon} />
          </Link>
        </Tooltip>
        <Tooltip title={t("Logout")} placement="right">
          <div className={styles.link}>
            <LogoutIcon id="sidebar-link-logout" onClick={handleLogout} className={styles.icon} />
          </div>
        </Tooltip>
      </ul>
    </div>
  )
})

Sidebar.displayName = "Sidebar"
