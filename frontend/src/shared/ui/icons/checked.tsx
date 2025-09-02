import { CheckOutlined } from "@ant-design/icons"

interface CheckedIconProps {
  value: boolean
}
export const CheckedIcon = ({ value }: CheckedIconProps) => {
  return value ? <CheckOutlined /> : null
}
