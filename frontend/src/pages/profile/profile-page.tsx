import { EditOutlined } from "@ant-design/icons"
import { PageHeader } from "@ant-design/pro-layout"
import { Button, Card, Col, Divider, Layout, Row } from "antd"
import { MeContext } from "processes"
import { useContext } from "react"
import { useTranslation } from "react-i18next"
import { useDispatch } from "react-redux"
import { ProfileAvatar } from "widgets"

import { showEditProfileModal } from "entities/user/model"

import { ChangePassword } from "features/user/change-password/change-password"

import { Field } from "shared/ui"

import { EditProfileModal } from "widgets/user"

import styles from "./styles.module.css"

const { Content } = Layout

export const ProfileFields = ({ profile }: { profile: User }) => {
  const { t } = useTranslation()
  return (
    <>
      <Field title={t("Username")} value={profile.username} />
      <Field title={t("Email")} value={profile.email} />
      <Field title={t("First Name")} value={profile.first_name} />
      <Field title={t("Last Name")} value={profile.last_name} />
    </>
  )
}

export const ProfilePage = () => {
  const { t } = useTranslation()
  const dispatch = useDispatch()
  const { me } = useContext(MeContext)

  const handleClickEdit = () => {
    dispatch(showEditProfileModal())
  }

  return (
    <>
      <PageHeader title={t("Profile")} ghost={false} style={{ paddingBottom: 0 }}></PageHeader>
      <Row style={{ margin: "24px" }}>
        <Col flex="0 1 260px">
          <div className={styles.avatarWrapper}>
            <ProfileAvatar />
          </div>
        </Col>
        <Col flex={9}>
          <Content style={{ marginLeft: "24px" }}>
            <Card>
              <Row align={"middle"}>
                <Col flex={"auto"}>
                  <p style={{ margin: 0, fontSize: 18 }}>{t("General Details")}</p>
                </Col>
                <Col flex={"none"}>
                  <Button id="edit-profile" onClick={handleClickEdit} icon={<EditOutlined />}>
                    {t("Edit")}
                  </Button>
                  {me && <ChangePassword />}
                </Col>
              </Row>
              <Divider />
              {me && <ProfileFields profile={me} />}
            </Card>
          </Content>
        </Col>
      </Row>
      <EditProfileModal />
    </>
  )
}
