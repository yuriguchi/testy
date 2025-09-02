const CLEAR_USERNAMES = ["admin", "ci", "unknown"]

export const UserUsername = ({ username }: { username: string }) => {
  const isClear = CLEAR_USERNAMES.some((name) => name === username)

  if (isClear) return <span style={{ userSelect: "none" }}>{username}</span>

  return (
    <a href="#" rel="noreferrer">
      {username}
    </a>
  )
}
