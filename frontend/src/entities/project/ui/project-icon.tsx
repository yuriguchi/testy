import { Avatar } from "antd"

import { generateProjectIconTitle } from "entities/project/lib/generate-project-icon-title"

interface Props {
  name: string
  icon?: string | null
  size?: number
  dataTestId?: string
}

export const ProjectIcon = ({ icon, name, size = 40, dataTestId = "project-icon" }: Props) => {
  return (
    <Avatar
      style={{
        verticalAlign: "middle",
        width: size,
        height: size,
        fontSize: size / 2.7,
        lineHeight: `${size}px`,
        userSelect: "none",
        marginRight: 12,
      }}
      size="large"
      src={icon?.length ? icon : undefined}
      data-testid={dataTestId}
    >
      {!icon && generateProjectIconTitle(name)}
    </Avatar>
  )
}
