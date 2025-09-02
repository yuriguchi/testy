import { Col, Row } from "antd"
import { SystemMessages } from "widgets"

import { Auth } from "entities/auth/auth"

import { Copyright } from "shared/ui"

export const LoginPage = () => {
  return (
    <Row justify="center" align="middle" style={{ minHeight: "100vh", position: "relative" }}>
      <div style={{ position: "absolute", top: 0, width: "100%" }}>
        <SystemMessages />
      </div>
      <Col xl={6} lg={8} md={10} sm={12} xs={24}>
        <div>
          <h1 style={{ marginBottom: 24, textAlign: "center" }}>TestY</h1>
        </div>
        <Auth />
        <Copyright />
      </Col>
    </Row>
  )
}
