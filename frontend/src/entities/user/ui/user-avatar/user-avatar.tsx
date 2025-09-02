import { UserOutlined } from "@ant-design/icons"
import { Avatar } from "antd"

import styles from "./styles.module.css"

interface UserAvatarProps {
  avatar_link: string | null
  size?: number
  nonce?: number
}

export const UserAvatar = ({ avatar_link, nonce = 1, size = 32 }: UserAvatarProps) => {
  return (
    <div className={styles.image} style={{ minWidth: size, minHeight: size }}>
      {!avatar_link ? (
        <Avatar icon={<UserOutlined id="username-icon" />} size={size} />
      ) : (
        <img
          id="username-photo"
          src={`${avatar_link}?nonce=${nonce}`}
          alt="avatar"
          style={{ minWidth: size, width: size, height: size }}
          loading="lazy"
        />
      )}
    </div>
  )
}
