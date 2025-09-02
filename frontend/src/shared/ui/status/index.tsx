import { Tag } from "antd"

type StatusProps = Pick<Status, "id" | "color" | "name"> & {
  extraId?: string
  style?: React.CSSProperties
}

export const Status = ({ id, name, color, style, extraId }: StatusProps) => {
  return (
    <Tag
      className="status"
      color={color}
      id={`${extraId ? extraId + "-" : ""}status-${name}-${id}`}
      style={style}
    >
      {name?.toUpperCase()}
    </Tag>
  )
}

export const UntestedStatus = () => {
  return (
    <Tag className="status" color="default" id="status-untested">
      UNTESTED
    </Tag>
  )
}
