import { Layout } from "antd"

import { Copyright } from "shared/ui"

const { Footer } = Layout

export const FooterView = () => {
  return (
    <Footer style={{ textAlign: "center" }}>
      <Copyright />
    </Footer>
  )
}
