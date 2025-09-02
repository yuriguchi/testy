import { PlusOutlined } from "@ant-design/icons"
import { PageHeader } from "@ant-design/pro-layout"
import { Breadcrumb, Button, Layout, Space } from "antd"
import { useTranslation } from "react-i18next"
import { useDispatch } from "react-redux"
import { LayoutView } from "widgets"

import { useAppSelector } from "app/hooks"

import { selectUser } from "entities/auth/model"

import { showCreateUserModal } from "entities/user/model"

import { CreateEditUserModal, UsersTable } from "widgets/user"

const { Content } = Layout

export const UsersPage = () => {
  const { t } = useTranslation()
  const dispatch = useDispatch()
  const user = useAppSelector(selectUser)

  const breadcrumbItems = [
    <Breadcrumb.Item key="administration">{t("Administration")}</Breadcrumb.Item>,
    <Breadcrumb.Item key="users">{t("Users")}</Breadcrumb.Item>,
  ]

  const handleClick = () => {
    dispatch(showCreateUserModal())
  }

  return (
    <>
      <PageHeader
        breadcrumbRender={() => <Breadcrumb>{breadcrumbItems}</Breadcrumb>}
        title={t("Users")}
        ghost={false}
        style={{ paddingBottom: 0 }}
      ></PageHeader>

      <Content style={{ margin: "24px" }}>
        <CreateEditUserModal />

        <LayoutView style={{ padding: 24, minHeight: 360 }}>
          <Space style={{ display: "flex", justifyContent: "right" }}>
            {user?.is_superuser && (
              <Button
                id="create-user"
                onClick={handleClick}
                type={"primary"}
                icon={<PlusOutlined />}
                style={{ marginBottom: 16, float: "right" }}
              >
                {t("Create User")}
              </Button>
            )}
          </Space>
          <UsersTable />
        </LayoutView>
      </Content>
    </>
  )
}
