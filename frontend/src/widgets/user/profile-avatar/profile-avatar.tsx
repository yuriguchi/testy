import { Button, UploadFile, notification } from "antd"
import Upload, { RcFile, UploadChangeParam } from "antd/lib/upload"
import { Mutex } from "async-mutex"
import { MeContext } from "processes"
import { useContext, useState } from "react"
import { useTranslation } from "react-i18next"
import { Crop, PercentCrop, ReactCrop } from "react-image-crop"

import { useDeleteAvatarMutation, useUploadAvatarMutation } from "entities/user/api"
import { UserAvatar } from "entities/user/ui/user-avatar/user-avatar"

import { fileReader, getNumberToFixed } from "shared/libs"

import styles from "./styles.module.css"

interface RequestError {
  data: {
    errors: string[]
    status: number
  }
}

const mutex = new Mutex()

export const ProfileAvatar = () => {
  const { t } = useTranslation()
  const { me } = useContext(MeContext)

  const [nonce, setNonce] = useState(1)
  const [isEdit, setIsEdit] = useState(false)
  const [image, setImage] = useState<{ url: string; file: RcFile | null }>({
    url: "",
    file: null,
  })
  const [isLoading, setIsLoading] = useState(false)
  const [uploadAvatar] = useUploadAvatarMutation()
  const [deleteAvatar] = useDeleteAvatarMutation()
  const [percentCrop, setPercentCrop] = useState<PercentCrop>({
    unit: "%",
    x: 25,
    y: 25,
    width: 50,
    height: 50,
  })

  const onChange = async (info: UploadChangeParam<UploadFile<unknown>>) => {
    if (!info.file.originFileObj) return
    const file = await fileReader(info.file)

    setImage({
      url: file.url ?? "",
      file: file.file ?? null,
    })
    setIsEdit(true)
  }

  const beforeUpload = (file: RcFile) => {
    const isCorrectType = file.type === "image/png" || file.type === "image/jpeg"
    if (!isCorrectType) {
      notification.error({
        message: t("Error!"),
        description: `${file.name} is not a png or jpg file`,
      })
    }

    return isCorrectType || Upload.LIST_IGNORE
  }

  const handleChangeCrop = (_: Crop, percent: PercentCrop) => {
    setPercentCrop(percent)
  }

  const handleEditClick = () => {
    setImage({ url: "", file: null })
  }

  const handleDeleteClick = () => {
    deleteAvatar()
  }

  const handleSaveClick = async () => {
    setIsLoading(true)
    if (!image.file) return

    const floatCrop = {
      left: getNumberToFixed(percentCrop.x / 100, 6),
      right: getNumberToFixed(percentCrop.width / 100, 6),
      lower: getNumberToFixed(percentCrop.height / 100, 6),
      upper: getNumberToFixed(percentCrop.y / 100, 6),
    }

    const cropPositions: CropPositions = {
      left: floatCrop.left,
      right: getNumberToFixed(floatCrop.left + floatCrop.right, 6),
      lower: getNumberToFixed(floatCrop.lower + floatCrop.upper, 6),
      upper: floatCrop.upper,
    }

    const fmData = new FormData()
    fmData.append("avatar", image.file)
    fmData.append("crop", JSON.stringify(cropPositions))
    await mutex.waitForUnlock()
    const release = await mutex.acquire()
    try {
      await uploadAvatar(fmData).unwrap()

      notification.success({
        message: t("Success"),
        closable: true,
        description: t("Avatar was updated successfully"),
      })
      setNonce(nonce + 1)
    } catch (err) {
      const error = err as RequestError
      console.error(error)
      notification.error({
        message: t("Error!"),
        // eslint-disable-next-line @typescript-eslint/restrict-template-expressions
        description: `${error.data.errors[0]}. ${t("Showing detail in console log.")}`,
      })
    } finally {
      release()
      setIsLoading(false)
      setIsEdit(false)
    }
  }

  if (isEdit && image.url) {
    return (
      <div className={styles.editBlock}>
        <ReactCrop
          crop={percentCrop}
          onChange={handleChangeCrop}
          aspect={1}
          circularCrop
          disabled={false}
          minHeight={10}
          minWidth={10}
          keepSelection
        >
          <img id="profile-avatar-crop-image" src={image.url} />
        </ReactCrop>
        <div className={styles.btns}>
          <Button onClick={handleEditClick} id="profile-avatar-edit-button">
            {t("Edit")}
          </Button>
          <Button
            type="primary"
            onClick={handleSaveClick}
            loading={isLoading}
            id="profile-avatar-save-button"
          >
            {t("Save")}
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.wrapper}>
      <div className={styles.avatarBlock}>
        {me && (
          <div className={styles.imageView}>
            <UserAvatar avatar_link={me.avatar_link} size={180} nonce={nonce} />
          </div>
        )}
      </div>
      <div className={styles.wrapperBtns}>
        <div className={styles.btns}>
          <Upload
            name="avatar"
            showUploadList={false}
            onChange={onChange}
            style={{ width: 180 }}
            customRequest={() => {}}
            beforeUpload={beforeUpload}
            id="profile-avatar-upload"
          >
            <Button id="profile-avatar-edit-button">{t("Edit")}</Button>
          </Upload>

          {me?.avatar_link && (
            <Button danger onClick={handleDeleteClick} id="profile-avatar-delete-button">
              {t("Delete")}
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
