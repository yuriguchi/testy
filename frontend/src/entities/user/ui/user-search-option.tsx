import { UserAvatar } from "./user-avatar/user-avatar"

interface Props {
  user: User
}

export const UserSearchOption = ({ user }: Props) => {
  return (
    <div style={{ display: "flex", alignItems: "center", flexDirection: "row", gap: 8 }}>
      <div style={{ width: 20, height: 20 }}>
        <UserAvatar avatar_link={user.avatar_link} size={20} />
      </div>
      <span>{user.username}</span>
    </div>
  )
}
