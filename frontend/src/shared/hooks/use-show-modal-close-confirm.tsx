import { Modal } from "antd"
import { useTranslation } from "react-i18next"

export const useShowModalCloseConfirm = () => {
  const { t } = useTranslation()

  const showModal = (cb: () => void) => {
    Modal.confirm({
      title: t("Do you want to close?"),
      content: t("You will lose your data if you continue!"),
      okText: t("Ok"),
      cancelText: t("Cancel"),
      onOk: () => cb(),
      okButtonProps: { "data-testid": "button-confirm" },
      cancelButtonProps: { "data-testid": "button-cancel" },
    })
  }

  return { showModal }
}
