import { Alert, Button, Checkbox, Form, Input } from "antd"
import { Controller } from "react-hook-form"
import { useTranslation } from "react-i18next"

import { useAuthLogic } from "./model/Auth.logic"

export const Auth = () => {
  const { t } = useTranslation()
  const { control, errMsg, onSubmit, isLoading } = useAuthLogic()

  return (
    <>
      {errMsg ? <Alert style={{ marginBottom: 24 }} description={errMsg} type="error" /> : null}

      <Form onFinish={onSubmit} layout="vertical">
        <Form.Item label={t("Username")}>
          <Controller
            name="username"
            control={control}
            render={({ field }) => <Input {...field} />}
          />
        </Form.Item>
        <Form.Item label={t("Password")} name="password" style={{ marginBottom: 8 }}>
          <Controller
            name="password"
            control={control}
            render={({ field }) => <Input.Password {...field} />}
          />
        </Form.Item>
        <Form.Item name="remember_me">
          <Controller
            name="remember_me"
            control={control}
            render={({ field }) => (
              <Checkbox
                {...field}
                checked={field.value}
                onChange={(e) => field.onChange(e.target.checked)}
              >
                {t("Remember me")}
              </Checkbox>
            )}
          />
        </Form.Item>
        <Form.Item>
          <Button
            id="login-btn"
            size="large"
            type="primary"
            htmlType="submit"
            block
            loading={isLoading}
          >
            {t("Login")}
          </Button>
        </Form.Item>
      </Form>
    </>
  )
}
