import { Flex, Select } from "antd"
import { useTranslation } from "react-i18next"

import EnIcon from "shared/assets/icons/en.svg?react"
import RuIcon from "shared/assets/icons/ru.svg?react"
import { config } from "shared/config"
import { useCacheState } from "shared/hooks"

import styles from "./styles.module.css"

const icons = {
  ru: <RuIcon width={24} />,
  en: <EnIcon width={24} />,
}

const options = [
  {
    label: "Русский",
    value: "ru",
  },
  {
    label: "English",
    value: "en",
  },
]

export const ChangeLang = () => {
  const { i18n } = useTranslation()
  const [value, update] = useCacheState("lang", config.defaultLang)

  const handleChange = (newLang: string[]) => {
    const nextLang = newLang as unknown as string
    update(nextLang)
    i18n.changeLanguage(nextLang)
  }

  return (
    <Select
      className={styles.select}
      defaultValue={[value]}
      onChange={handleChange}
      options={options}
      labelRender={(label) => {
        return (
          <Flex align="center" gap={8} style={{ maxHeight: 22 }}>
            {/* @ts-ignore */}
            <span role="img" aria-label={label.label} className={styles.label}>
              {/* @ts-ignore */}
              {icons[label.value]}
            </span>
            <span>{label.label}</span>
          </Flex>
        )
      }}
      optionRender={(option) => (
        <Flex align="center" gap={8} style={{ maxHeight: 22 }}>
          <span role="img" aria-label={option.data.label} className={styles.label}>
            {/* @ts-ignore */}
            {icons[option.value]}
          </span>
          <span>{option.data.label}</span>
        </Flex>
      )}
    />
  )
}
